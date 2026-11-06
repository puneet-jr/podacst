"""Actual DB/local-model evaluation; judgment spans frozen independently of retrieval."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
import statistics
import time

from sqlalchemy import text

from backend.app.config import load_settings
from backend.app.db import make_engine
from backend.app.embedding import OllamaEmbedder
from backend.app.retrieval import RETRIEVAL_VERSION, SearchRequest, search


def metrics(retrieved, relevant, anchor_ids):
    ids = [str(p.id) for p in retrieved]
    hits=[int(i in relevant) for i in ids]
    ideal=sum(1/math.log2(i+2) for i in range(min(8,len(relevant))))
    return {'recall_at_8':len(set(ids)&relevant)/len(relevant),
            'mrr_at_8':next((1/(i+1) for i,hit in enumerate(hits) if hit),0.),
            'ndcg_at_8':sum(hit/math.log2(i+2) for i,hit in enumerate(hits))/ideal,
            'anchor_recall_at_8':sum(bool(set(ids)&set(group)) for group in anchor_ids)/len(anchor_ids)}


def resolve_judgments(engine, cases):
    resolved={}
    with engine.connect() as c:
        for case in cases:
            groups=[]
            for anchor in case['evidence']:
                version=c.execute(text('''SELECT e.id,e.current_version,v.original_text FROM episodes e
                 JOIN episode_versions v ON v.episode_id=e.id AND v.version=e.current_version
                 WHERE e.source_path=:path AND e.source_hash=:hash AND e.deleted_at IS NULL'''),
                 {'path':anchor['source_path'],'hash':anchor['source_hash']}).mappings().one()
                actual=version['original_text'][anchor['char_start']:anchor['char_end']]
                if sha256(actual.encode()).hexdigest()!=anchor['text_sha256']:raise ValueError('judgment_source_span_mismatch')
                ids=list(c.scalars(text('''SELECT id FROM chunks WHERE active AND episode_id=:episode AND version=:version
                  AND source_hash=:hash AND char_start<=:start AND char_end>=:end ORDER BY id'''),
                  {'episode':version['id'],'version':version['current_version'],'hash':anchor['source_hash'],'start':anchor['char_start'],'end':anchor['char_end']}))
                if not ids:raise ValueError('judgment_has_no_complete_passage')
                groups.append([str(i) for i in ids])
            resolved[case['id']]={'groups':groups,'relevant_ids':sorted(set(i for group in groups for i in group))}
    return resolved


def validate_passages(engine, passages):
    with engine.connect() as c:
        for p in passages:
            row=c.execute(text('''SELECT c.*,e.source_path,e.current_version,v.original_text AS full_original
             FROM chunks c JOIN episodes e ON e.id=c.episode_id JOIN episode_versions v ON v.episode_id=c.episode_id AND v.version=c.version
             WHERE c.id=:id AND c.active AND e.deleted_at IS NULL'''),{'id':p.id}).mappings().one()
            if not (row['current_version']==p.version==row['version'] and row['source_path']==p.source_path and row['source_hash']==p.source_hash
                    and row['full_original'][p.char_start:p.char_end]==p.original_text==row['original_text']
                    and sha256(p.original_text.encode()).hexdigest()==p.text_sha256):raise ValueError('returned_passage_integrity_mismatch')


def percentile(values,fraction):
    return sorted(values)[max(0,math.ceil(len(values)*fraction)-1)]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cases',default='eval/retrieval-cases.json')
    parser.add_argument('--config',default='eval/retrieval-local-v3.json')
    parser.add_argument('--split',required=True,choices=['tuning','held_out','unsupported'])
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    case_path,config_path=Path(args.cases),Path(args.config)
    judgments=json.loads(case_path.read_text());config=json.loads(config_path.read_text());config_revision=config.pop('revision')
    settings=load_settings();engine=make_engine(settings)
    output=Path(args.output);output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    report={'started_at':datetime.now(timezone.utc).isoformat(),'split':args.split,'case_file_sha256':sha256(case_path.read_bytes()).hexdigest(),
      'config_sha256':sha256(config_path.read_bytes()).hexdigest(),'config_revision':config_revision,'config':config,'corpus_revision':judgments['corpus_revision'],
      'scope':judgments['scope'],'retrieval_version':RETRIEVAL_VERSION,'actual_postgresql':True,'actual_local_ollama':True,'cloud_inference':False,'results':[]}
    try:
        cases=judgments['unsupported'] if args.split=='unsupported' else [c for c in judgments['cases'] if c['split']==args.split]
        resolved={} if args.split=='unsupported' else resolve_judgments(engine,cases)
        (output/'resolved-judgments.json').write_text(json.dumps(resolved,indent=2)+'\n')
        # Explicit measured warmup, excluded from warm-query summaries.
        warm=time.monotonic();embedder=OllamaEmbedder(settings)
        try: report['embedding_digest']=embedder.preflight()
        finally:embedder.close()
        report['model_warmup_ms']=(time.monotonic()-warm)*1000
        modes=['sparse','dense','hybrid']
        for index,case in enumerate(cases):
            for mode in modes[index%3:]+modes[:index%3]:
                request=SearchRequest(query=case.get('resolved_query',case['question']),mode=mode,**case.get('filters',{}),**config)
                result=search(engine,settings,request)
                validate_passages(engine,result.passages)
                entry={'case_id':case['id'],'mode':mode,'scoped':bool(case.get('filters')),'kind':case.get('kind','unsupported'),
                    'status':result.status,'support_verified':result.support_verified,'count':len(result.passages),'estimated_tokens':result.estimated_tokens,
                    'timings_ms':result.timings_ms,'candidate_counts':result.candidate_counts,'corpus':result.corpus,
                    'source_integrity_passed':True,'passages':[p.model_dump(mode='json',exclude={'original_text'}) for p in result.passages]}
                if args.split!='unsupported':
                    gold=resolved[case['id']];entry['metrics']=metrics(result.passages,set(gold['relevant_ids']),gold['groups'])
                else:entry['semantic_support_review']='pending direct source inspection; nearest-neighbor output is not support'
                report['results'].append(entry)
                with (output/'results.jsonl').open('a') as f:f.write(json.dumps(entry)+'\n')
                print(json.dumps({'event':'retrieval_case','case_id':case['id'],'mode':mode,'count':entry['count'],'metrics':entry.get('metrics'),'duration_ms':result.timings_ms['total']}),flush=True)
        summary={}
        for mode in modes:
            entries=[r for r in report['results'] if r['mode']==mode]
            times=[r['timings_ms']['total'] for r in entries]
            item={'n':len(entries),'mean_count':statistics.mean(r['count'] for r in entries),'min_count':min(r['count'] for r in entries),'max_count':max(r['count'] for r in entries),
                'latency_ms_median':statistics.median(times),'latency_ms_p95_nearest_rank':percentile(times,.95),'latency_ms_max':max(times)}
            if args.split!='unsupported':
                for metric in ('recall_at_8','mrr_at_8','ndcg_at_8','anchor_recall_at_8'):item[metric]=statistics.mean(r['metrics'][metric] for r in entries)
                item['by_scope']={scope:{'n':len(sub),'recall_at_8':statistics.mean(r['metrics']['recall_at_8'] for r in sub)} for scope in ('scoped','unscoped') if (sub:=[r for r in entries if r['scoped']==(scope=='scoped')])}
            summary[mode]=item
        report['summary']=summary;report['passed']=all(r['source_integrity_passed'] for r in report['results']) and len(report['results'])==len(cases)*3
    except Exception as exc:
        report['passed']=False;report['error_type']=type(exc).__name__
        report['error_code']=str(exc) if isinstance(exc,ValueError) else 'evaluation_failed_see_safe_diagnostics'
        raise
    finally:
        engine.dispose();report['completed_at']=datetime.now(timezone.utc).isoformat();report['duration_seconds']=time.monotonic()-started
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'event':'retrieval_evaluation_summary','output':str(output),'passed':report['passed'],'summary':report.get('summary'),'duration_seconds':report['duration_seconds']}),flush=True)


if __name__=='__main__':main()
