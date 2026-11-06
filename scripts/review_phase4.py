"""Evidence/static audit; engineering gate and measured quality are distinct."""
import ast
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

from review_phase3 import source_files

ROOT=Path(__file__).resolve().parent.parent
EVIDENCE=ROOT/'docs/agent-transcripts/phase-04'


def main():
    checks=[]
    def check(name,condition,detail):checks.append({'name':name,'passed':bool(condition),'detail':detail})
    rows=[json.loads(l) for l in (EVIDENCE/'commands.jsonl').read_text().splitlines()]
    contract=[r for r in rows if r['command'][-1:]==['backend.contract_check']][-1]
    check('Final actual PostgreSQL/local fixture suite',contract['exit_code']==0 and 'Ran 49 tests' in contract['stderr'] and '\nOK\n' in contract['stderr'],'49 tests; 33 unit/parser/mock, 16 PostgreSQL/API; injection separate from actual provider calls')
    metric=[r for r in rows if 'test_metrics.py' in r['command']][-1]
    check('Separate hand-calculated metric checks',metric['exit_code']==0 and 'Ran 3 tests' in metric['stderr'],'Three known-list checks on host, not live integrations')
    live=json.loads((EVIDENCE/'live-api.json').read_text())
    check('Actual HTTP/API/source/persistence proofs',live['passed'] and len(live['checks'])==9 and all(r['passed'] for r in live['checks']),'Nine checks, real local hybrid; saved conversation hashes match Phase 3')
    frozen=json.loads((EVIDENCE/'judgment-freeze.json').read_text())
    cases_path=ROOT/frozen['path'];cases=json.loads(cases_path.read_text())
    check('Judgments stayed frozen',sha256(cases_path.read_bytes()).hexdigest()==frozen['sha256'] and len(cases['cases'])==24 and len(cases['unsupported'])==4,{'sha256':frozen['sha256'],'tuning':16,'held_out':8,'source_anchors':32})
    selection=json.loads((ROOT/'eval/retrieval-selection.json').read_text())
    reports={name:json.loads((EVIDENCE/'container-evidence'/name/'report.json').read_text()) for name in ['tuning-v1','tuning-v2-local','tuning-v3-local','held-out-v3-first','unsupported-v3-first']}
    check('Candidate selected before held-out, unchanged',all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in selection['files'].items()) and datetime.fromisoformat(selection['frozen_at'])<datetime.fromisoformat(reports['held-out-v3-first']['started_at']),'No source/config/judgment changes after holdout; sparse frozen from tuning')
    expected={'tuning-v1':48,'tuning-v2-local':48,'tuning-v3-local':48,'held-out-v3-first':24,'unsupported-v3-first':12}
    check('Actual evaluations and exact source integrity',all(r['passed'] and len(r['results'])==expected[name] and r['case_file_sha256']==frozen['sha256'] and all(x['source_integrity_passed'] for x in r['results']) for name,r in reports.items()),{'actual_searches_by_attempt':expected,'note':'Successful execution/source proof is not a quality pass'})
    summary=json.loads((EVIDENCE/'metrics-summary.json').read_text())
    check('Quality failure disclosed accurately',not summary['selected_default_quality_target_met'] and summary['held_out']['sparse']['recall_at_8']==.625 and summary['all_24_descriptive_only']['hybrid']['recall_at_8']==.75,{'selected_default_held_out_recall':.625,'all_case_descriptive_hybrid_recall':.75,'quality_target_met':False})
    check('Unsupported diagnostics are not called abstentions',all(r['status']=='review_required' and not r['support_verified'] and r['count']>0 for r in reports['unsupported-v3-first']['results']),'12 nonempty candidate packets; sampled source review, no generated answers')
    baseline=json.loads((EVIDENCE/'prior-evidence-baseline.json').read_text())['files']
    changed=[p for p,h in baseline.items() if sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    check('Original spike and Phase 1–3 evidence preserved',not changed,{'files':len(baseline),'changed':changed})
    installed_row=[r for r in rows if any('files=[p for base in' in part for part in r['command'])][-1]
    installed=json.loads(installed_row['stdout'])
    mismatches=[p for p,h in installed.items() if sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    check('Tested backend/agent matches workspace',not mismatches,{'files':len(installed),'mismatches':mismatches})
    files=source_files()
    syntax=[];links=[]
    for p in files:
        if p.suffix=='.py':
            try:ast.parse(p.read_text())
            except SyntaxError:syntax.append(str(p.relative_to(ROOT)))
        if p.suffix=='.md' and p.name not in {'LENNY_BUILD_FLOW.md','LENNY_CODEX_PROMPTS.md'}:
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                target=target.strip('<>').split('#')[0]
                if target and '://' not in target and not target.startswith('mailto:') and not (p.parent/target).exists():links.append({'file':str(p.relative_to(ROOT)),'target':target})
    check('Current source syntax and documentation links',not syntax and not links,{'syntax_errors':syntax,'broken_links':links})
    ids=re.findall(r'^\| ((?:FD|API|AG|SES|DB|MOD|KB|RAG|ESS|ART|OPS|DEL)-\d{2}) \|',(ROOT/'docs/requirements.md').read_text(),re.M)
    check('All requirement IDs retained',len(ids)==len(set(ids))==29,{'count':len(ids)})
    secret=next((l.split('=',1)[1].strip().strip('"\'') for l in (ROOT/'.env').read_text().splitlines() if l.startswith('POSTGRES_PASSWORD=')),None)
    suspects=[str(p.relative_to(ROOT)) for p in [*files,*[p for p in EVIDENCE.rglob('*') if p.is_file()]] if secret and secret.encode() in p.read_bytes()]
    forbidden=[str(p.relative_to(ROOT)) for p in files if p.suffix=='.pdf' or p.name.casefold()=='transcript.md']
    check('Generated credential/private corpus absent from source/evidence',bool(secret) and not suspects and not forbidden,{'suspect_paths':suspects,'private_paths':forbidden,'limit':'Exact generated credential check, not full security audit'})
    json_errors=[]
    for p in EVIDENCE.rglob('*'):
        try:
            if p.suffix=='.json':json.loads(p.read_text())
            if p.suffix=='.jsonl':
                for line in p.read_text().splitlines():
                    if line.strip():json.loads(line)
        except (ValueError,UnicodeError):json_errors.append(str(p.relative_to(ROOT)))
    check('Saved JSON evidence parses',not json_errors,json_errors)
    images=json.loads([r for r in rows if r['command'][-3:]==['images','--format','json']][-1]['stdout'])
    manifest={'created_at':datetime.now(timezone.utc).isoformat(),'revision':'No Git repository initialized; SHA-256 final source identity, actual images and separate runtime evidence.','images':images,'files':[{'path':str(p.relative_to(ROOT)),'sha256':sha256(p.read_bytes()).hexdigest()} for p in files]}
    (EVIDENCE/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    result={'captured_at':datetime.now(timezone.utc).isoformat(),'engineering_gate_passed':all(c['passed'] for c in checks),'quality_target_met':False,'checks':checks,
      'limits':['9/303 episodes indexed; 294 remain','Sparse default held-out recall62.5%, selection instability/unscoped/synthesis defects open','No generated answer support/abstention/routing/essay/SC-01 outcomes','Labels are incomplete and not independent expert judgments; heldout now observed','Browser/rights/cloud/full coding export/clean evaluator gaps remain']}
    (EVIDENCE/'final-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not result['engineering_gate_passed']:raise SystemExit(1)


if __name__=='__main__':main()
