"""Final read-only evidence/source/secret/link audit; does not rerun inference or tests."""
import ast
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

import httpx

BASE=Path('docs/agent-transcripts/phase-05')
live=BASE/'live-20261106T081843/results.jsonl'
rows=[r for r in map(json.loads,live.read_text().splitlines()) if r.get('run')]
commands=[json.loads(line) for line in (BASE/'commands.jsonl').read_text().splitlines()]
contract=[r for r in commands if 'backend.contract_check' in r['command']][-1]
policy=[r for r in commands if 'agent/test_conversation_policy.ts' in r['command']][-1]
final_live=[r for r in commands if 'scripts/live_phase5.py' in r['command']][-1]
protected=json.loads((BASE/'preservation-baseline.json').read_text())
changed=[p for p,h in protected['files'].items() if not Path(p).is_file() or sha256(Path(p).read_bytes()).hexdigest()!=h]
runtime=json.loads((BASE/'runtime-review.json').read_text())
support=json.loads((BASE/'support-review.json').read_text())
opened=json.loads((BASE/'opened-sources.json').read_text())
reopened=json.loads((BASE/'lifecycle-20261106T074854/restart-after.json').read_text())
hostile=json.loads((BASE/'hostile-source.json').read_text())
report_paths=[Path(p) for p in ('README.md','AGENTS.md','docs/progress.md','docs/PRD.md','docs/requirements.md','docs/architecture.md','docs/decisions.md','docs/risks.md','docs/assumptions.md','docs/environment.md','docs/design.md','docs/test-plan.md','docs/provenance.md','docs/phase-05-report.md','docs/phase-05-operations.md','docs/agent-transcripts/README.md','docs/agent-transcripts/phase-05/README.md')]
source_paths=set(report_paths+[Path('compose.yaml')])
for directory,suffixes in [('backend',{'.py','.lock','.ini'}),('agent',{'.ts','.json'}),('frontend',{'.tsx','.ts','.css','.json','.html','.conf'}),('scripts',{'.py'})]:
    for p in Path(directory).rglob('*'):
        if p.is_file() and p.suffix in suffixes and not {'node_modules','dist','__pycache__'} & set(p.parts):source_paths.add(p)
for p in [Path('backend/Dockerfile'),Path('frontend/Dockerfile'),Path('.dockerignore'),Path('.gitignore')]:source_paths.add(p)
hashes={str(p):sha256(p.read_bytes()).hexdigest() for p in sorted(source_paths)}
inside_code=r'''
from hashlib import sha256
from pathlib import Path
import json,sys
files=json.loads(sys.argv[1]);runs=json.loads(sys.argv[2]);hashes={p:sha256(Path(p).read_bytes()).hexdigest() for p in files};fresh=[]
for run in runs:
 f=Path('/app/evidence/private-chat')/run['id']/str(run['attempt'])/'stdout.jsonl'
 raw=f.read_bytes();frames=[json.loads(l) for l in raw.splitlines()]
 states=[e['data'] for e in frames if e.get('type')=='response' and e.get('command')=='get_state' and e.get('success')]
 diagnostics=[]
 for l in f.with_name('stderr.log').read_text().splitlines():
  try:diagnostics.append(json.loads(l))
  except ValueError:pass
 fresh.append({'run_id':run['id'],'initial_message_count':states[0].get('messageCount') if states else None,'pi_session_id':states[0].get('sessionId') if states else None,'provider':states[0].get('model',{}).get('provider') if states else None,'model':states[0].get('model',{}).get('id') if states else None,'actual_tool_start_count':sum(e.get('type')=='tool_execution_start' for e in frames),'provider_requests':sum(d.get('event')=='provider_request' for d in diagnostics),'active_tools':[d.get('active') for d in diagnostics if d.get('event')=='tool_policy'],'normalized_requests':sum(d.get('event')=='text_tool_call_normalized' for d in diagnostics),'stdout_ends_lf':raw.endswith(b'\n')})
print(json.dumps({'hashes':hashes,'fresh_protocols':fresh}))
'''
image_files=[p for p in hashes if p.startswith('backend/') and p.endswith(('.py','.lock','.ini')) or p in {'agent/conversation.ts','agent/conversation_policy.ts','agent/test_conversation_policy.ts','agent/retrieval.ts','agent/fixture.json','agent/package.json','agent/package-lock.json'}]
process=subprocess.run([sys.executable,'scripts/docker.py','compose','exec','-T','api','python','-c',inside_code,json.dumps(image_files),json.dumps([{'id':r['run']['id'],'attempt':r['run']['attempt']} for r in rows])],capture_output=True,text=True,timeout=25)
if process.returncode:raise RuntimeError('Runtime source/protocol audit failed')
inside=json.loads(process.stdout)
mismatch=[p for p,h in inside['hashes'].items() if hashes[p]!=h]
bad_links=[]
for p in report_paths:
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        target=target.strip('<>').split('#',1)[0]
        if not target or '://' in target or target.startswith('#'):continue
        if not (p.parent/target).exists():bad_links.append({'file':str(p),'target':target})
secrets=[]
if Path('.env').exists():
    for line in Path('.env').read_text().splitlines():
        if '=' not in line or line.lstrip().startswith('#'):continue
        key,value=line.split('=',1);value=value.strip().strip('"\'')
        if any(word in key for word in ('PASSWORD','API_KEY','SECRET','TOKEN')) and len(value)>=12:secrets.append(value.encode())
scan_paths=set(source_paths)
for p in BASE.rglob('*'):
    if p.is_file() and p.suffix in {'.json','.jsonl','.md'}:scan_paths.add(p)
secret_matches=[str(p) for p in sorted(scan_paths) if any(value in p.read_bytes() for value in secrets)]
with httpx.Client(base_url='http://127.0.0.1:8080',trust_env=False,timeout=20) as client:
    health=client.get('/api/health/ready');health.raise_for_status()
    index=client.get('/');index.raise_for_status()
    scripts=re.findall(r'<script[^>]+src="([^"]+)"',index.text)
    served=[{'path':path,'status':client.get(path).status_code} for path in scripts]
tests={p.name:sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_') for n in ast.walk(ast.parse(p.read_text()))) for p in Path('backend/tests').glob('test_*.py')}
checks={
 'final_contract_completed':contract['exit_code']==0 and 'Ran 66 tests' in contract['stderr'] and '\nOK\n' in contract['stderr'],
 'policy_tests_completed':policy['exit_code']==0,
 'final_live_completed_despite_interruption':final_live['exit_code']==0 and len(rows)==4 and all(r['passed_automatic_contract_checks'] for r in rows),
 'all_final_runs_hybrid':all(r['run']['retrieval_mode']=='hybrid' for r in rows),
 'fresh_pi_sessions_zero_history':len({p['pi_session_id'] for p in inside['fresh_protocols']})==4 and all(p['initial_message_count']==0 and p['provider']=='ollama-local' and p['model']=='qwen3:0.6b' for p in inside['fresh_protocols']),
 'real_controlled_tool_and_bounds':all(p['actual_tool_start_count']==1 and p['provider_requests']==2 and p['stdout_ends_lf'] and p['active_tools']==[['search_transcripts']] for p in inside['fresh_protocols']),
 'follow_up_uses_prior_user_and_fresh_evidence':rows[1]['run']['context_message_ids']==[rows[0]['run']['user_message_id']] and set(rows[0]['run']['metadata']['retrieved_passage_ids']).isdisjoint(rows[1]['run']['metadata']['retrieved_passage_ids']),
 'independent_session_no_inherited_context':rows[3]['run']['session_id']!=rows[0]['run']['session_id'] and not rows[3]['run']['context_message_ids'],
 'private_gap_policy_recorded_honestly':rows[2]['run']['metadata']['private_fact_guard_applied'] and rows[2]['run']['metadata']['model_selection']['status']=='answered' and rows[2]['run']['output']['status']=='insufficient_evidence' and not rows[2]['run']['output']['source_labels'],
 'all_final_citations_opened':len(opened['opened_citations'])==3 and all(s['http_status']==200 and s['exact_quotes'] for s in opened['opened_citations']),
 'manual_quality_failure_disclosed':support['cases'][-1]['assessment']=='isolation_pass_semantic_answer_incomplete',
 'restart_and_hostile_checks_recorded':reopened['passed'] and hostile['passed'],
 'prior_files_preserved':not changed,
 'runtime_preservation_and_framing':runtime['passed'],
 'runtime_matches_final_source':not mismatch,
 'documentation_links_valid':not bad_links,
 'no_configured_secrets_in_shared_files':not secret_matches,
 'web_health_and_assets_served':health.json()['checks']['corpus']['active_episodes']==9 and not health.json()['product_ready'] and bool(served) and all(s['status']==200 for s in served),
}
manifest={'captured_at':datetime.now(timezone.utc).isoformat(),'git_revision':None,'identity_note':'Workspace has no Git repository; source hashes and actual API image identify this gate. Private state/build output excluded.','files':hashes,'api_image_id':runtime['api_image_id']}
(BASE/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result={'captured_at':manifest['captured_at'],'checks':checks,'passed_evidence_audit':all(checks.values()),'local_api_gate':'passed_for_demonstrated_bounded_extractive_workflow','browser_gate':'blocked_before_connection','general_answer_quality':'not_passed; independent answer incomplete and model private-data abstention failed','prompt_06':'not_started; explicit user go-ahead required','fresh_protocols':inside['fresh_protocols'],'runtime_source_mismatches':mismatch,'protected_prior_files_changed':changed,'broken_documentation_links':bad_links,'configured_secret_matches':secret_matches,'test_method_counts':tests,'served_assets':served,'resumed_verification':'No model/test rerun needed: original final suite and live command completed exit0. Only read-only audits/source opening and documentation completed.','limits':'This audit cannot establish browser behavior, comprehensive security, semantic adequacy for arbitrary requests or complete coding-conversation export.'}
(BASE/'final-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if not all(checks.values()):raise SystemExit(1)
