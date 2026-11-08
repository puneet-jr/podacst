"""One no-retry plain-Markdown section probe from the saved owned outline/sources.

The normal essay rubric is not weakened: this is a section probe, never a completed
essay. Original source bodies stay in PostgreSQL/private traces; stdout is a safe
projection plus the actual model-written section for direct support review.
"""
import asyncio
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time
from uuid import UUID,uuid4

from sqlalchemy import text
from backend.app.config import load_settings
from backend.app.db import make_engine
from backend.app.essays import EssayService,load_essay,prepare_essay,save_progress,read_essay_sources
from backend.app.writing import EssayCreate,EssayError,POLICY,assemble,parse_markdown_section,validate_essay,word_count

ORIGIN_SESSION=UUID('1dca09bc-7a12-4118-b6b9-4322f85d1397')
ORIGIN_RUN=UUID('bf8f692a-a48f-43b4-b116-0f8755c799e7')
SECTION_INDEX=1  # Saved outline section2, Foundation, backed by S2/S3.


async def main():
    settings=load_settings();engine=make_engine(settings)
    origin=load_essay(engine,settings,ORIGIN_SESSION,ORIGIN_RUN)
    saved_sources=read_essay_sources(engine,settings,ORIGIN_SESSION,ORIGIN_RUN)
    by_label={s['source_label']:s for s in saved_sources}
    section=origin['outline']['sections'][SECTION_INDEX];labels=section['source_ids']
    if set(labels)-set(by_label):raise RuntimeError('Saved outline sources do not resolve')
    sid=uuid4()
    with engine.begin() as c:
        running=c.scalar(text("SELECT (SELECT count(*) FROM answer_runs WHERE status='running')+(SELECT count(*) FROM essay_runs WHERE status='running')"))
        if running:raise RuntimeError('Another application generation is active; no model request made')
        c.execute(text('INSERT INTO sessions(id,user_id,title) VALUES(:id,:user,:title)'),{'id':sid,'user':settings.local_user_id,'title':'Phase6 single plain-Markdown section probe'})
    body=EssayCreate(**origin['request'],client_message_id=uuid4())
    run,_=prepare_essay(engine,settings,sid,body)
    with engine.begin() as c:
        c.execute(text('INSERT INTO essay_sources(run_id,source_label,chunk_id,original_text,source_metadata,quote_spans) SELECT :new,source_label,chunk_id,original_text,source_metadata,quote_spans FROM essay_sources WHERE run_id=:old'),{'new':run['id'],'old':ORIGIN_RUN})
    metadata={**run['metadata'],'stages':[],'repairs_used':0,'test_kind':'single_plain_markdown_section','origin_run_id':str(ORIGIN_RUN),'section_index':SECTION_INDEX+1,'retrieval_mode':'saved_hybrid_snapshot','no_retry':True}
    save_progress(engine,run['id'],outline=origin['outline'],metadata=metadata)
    packet={'retrieval_mode':'hybrid_snapshot','untrusted_source_data':True,'sources':[{'id':label,'guest':by_label[label]['metadata']['guest'],'title':by_label[label]['metadata']['title'][:110],'original_text':by_label[label]['original_text']} for label in labels]}
    async def snapshot():return packet
    req=origin['request'];citation_text=', '.join('['+label+']' for label in labels)
    prompt=json.dumps({'topic':req['topic'],'audience':req['audience'],'constraints':req['constraints']},ensure_ascii=False)+f'\nUse the SAVED outline. Write ONLY section {SECTION_INDEX+1}: '+section['heading']+'\nPurpose: '+section['purpose']+f'\nTarget210 words. Write body-only plain Markdown, no JSON, code fences, title, or repeated heading. The only valid citations are {citation_text}. Cite each factual paragraph with the exact supplied labels. Keep case-specific qualifications; no invented statistics, quotes, causal promises or anecdotes. Label any proposed user action Application:. Do not summarize or draft the remaining essay.'
    service=EssayService(engine,settings,asyncio.Lock());started=time.monotonic();raw='';failure=None;parsed='';checks={};validation=None
    try:
        raw=await service.stage(run,'section-2-plain-markdown-probe',prompt,snapshot,{},POLICY['section_output_tokens'],metadata)
        parsed=parse_markdown_section(raw)
        item={'heading':section['heading'],'body':parsed,'source_ids':labels,'target_words':210,'error':None}
        sources={label:{**by_label[label]['metadata'],'original_text':by_label[label]['original_text']} for label in labels}
        validation=validate_essay(origin['outline']['title'],[item],sources)
        global_only={'word_count_outside_range','incomplete_sections','missing_action_bullets','bold_not_selective'}
        section_errors=[e for e in validation['errors'] if e['code'] not in global_only]
        stop=metadata['stages'][-1].get('stop_reason')
        checks={'plain_markdown':True,'original_section_floor_80_words':word_count(parsed)>=80,'citation_and_paragraph_screens':not section_errors,'not_output_truncated':stop not in {'length','maxTokens'},'saved_ids_resolve':True}
        save_progress(engine,run['id'],sections=[item],draft_md=assemble(origin['outline']['title'],[item]),validation=validation)
    except Exception as exc:
        failure={'code':getattr(exc,'code','section_probe_error'),'type':type(exc).__name__}
        if metadata['stages']:raw=metadata['stages'][-1].get('model_text') or ''
    finally:
        metadata['elapsed_seconds']=time.monotonic()-started
        passed=bool(checks) and all(checks.values()) and failure is None
        # This probe cannot become a full essay or pass the original total-count gate.
        save_progress(engine,run['id'],status='failed',error_code='section_probe_only_manual_review_pending' if passed else (failure or {}).get('code','section_probe_failed'),metadata=metadata)
        result={'captured_at':datetime.now(timezone.utc).isoformat(),'test_kind':'one_plain_markdown_section_no_retry','provider':'ollama-local','model':settings.generation_model,'probe_run_id':str(run['id']),'probe_session_id':str(sid),'origin_run_id':str(ORIGIN_RUN),'origin_session_id':str(ORIGIN_SESSION),'section_number':SECTION_INDEX+1,'heading':section['heading'],'purpose':section['purpose'],'target_words':210,'word_count':word_count(parsed or raw),'elapsed_seconds':metadata['elapsed_seconds'],'raw_markdown':raw,'checks':checks,'automatic_section_checks_passed':passed,'manual_factual_support':'pending direct review; no full essay will run without a support pass','failure':failure,'full_essay_gate':'not_tested; this is only one section','validation':validation,'stages':metadata['stages'],'source_passages':[{'source_label':label,'chunk_id':str(by_label[label]['chunk_id']),'source_metadata':by_label[label]['metadata'],'stored_text_sha256':sha256(by_label[label]['original_text'].encode()).hexdigest(),'snapshot_matches_recorded_text_hash':sha256(by_label[label]['original_text'].encode()).hexdigest()==by_label[label]['metadata']['text_sha256']} for label in labels]}
        destination=Path('/app/evidence/private-chat/markdown-tests')/str(run['id']);destination.mkdir(parents=True,exist_ok=False)
        (destination/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');(destination/'section.md').write_text(raw)
        print(json.dumps(result,ensure_ascii=False),flush=True);engine.dispose()
    if not passed:raise SystemExit(2)


if __name__=='__main__':asyncio.run(main())
