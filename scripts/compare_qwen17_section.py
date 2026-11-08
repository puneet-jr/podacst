"""Exactly one model-only comparison using the unchanged saved 0.6B section runner."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import httpx

ROOT=Path('docs/agent-transcripts/phase-06')
BASELINE=ROOT/'markdown-section-20261106T150144'
ORIGIN_SID='1dca09bc-7a12-4118-b6b9-4322f85d1397'
ORIGIN_RID='bf8f692a-a48f-43b4-b116-0f8755c799e7'
BASELINE_PROBE='d8aa563a-fd0d-4eb1-beef-7065a3aaa94f'
STAGE='section-2-plain-markdown-probe'

CODE_PROBE=r'''
from pathlib import Path
from hashlib import sha256
import json,sys
run_id=sys.argv[1];files=json.loads(sys.argv[2])
directory=Path('/app/evidence/private-chat/essays')/run_id/'section-2-plain-markdown-probe'
frames=[json.loads(l) for l in (directory/'stdout.jsonl').read_text().splitlines()]
messages=next(f['data']['messages'] for f in reversed(frames) if f.get('type')=='response' and f.get('command')=='get_messages' and f.get('success'))
prompts=[]
for m in messages:
 if m.get('role')!='user':continue
 content=m['content'];value=content if isinstance(content,str) else ''.join(b.get('text','') for b in content if b.get('type')=='text')
 prompts.append({'sha256':sha256(value.encode()).hexdigest(),'bytes':len(value.encode())})
diagnostics=[]
for line in (directory/'stderr.log').read_text().splitlines():
 try:
  e=json.loads(line)
  if e.get('event') in {'provider_request','tool_policy'}:diagnostics.append(e)
 except ValueError:pass
print(json.dumps({'user_prompts':prompts,'diagnostics':diagnostics,'runtime_source_sha256':{p:sha256(Path(p).read_bytes()).hexdigest() for p in files},'stdout_sha256':sha256((directory/'stdout.jsonl').read_bytes()).hexdigest(),'stderr_sha256':sha256((directory/'stderr.log').read_bytes()).hexdigest()}))
'''


def private_probe(rid,files):
    p=subprocess.run([sys.executable,'scripts/docker.py','compose','exec','-T','api','python','-c',CODE_PROBE,rid,json.dumps(files)],capture_output=True,text=True,check=True,timeout=25)
    return json.loads(p.stdout)


def main():
    if list(ROOT.glob('qwen17-section-*')):raise SystemExit('A 1.7B comparison directory already exists; inspect it rather than generating again.')
    baseline=json.loads((BASELINE/'result.json').read_text())
    preserve=json.loads(Path('.cache/qwen17-preservation-before.json').read_text())
    if any(sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in preserve.items()):raise RuntimeError('0.6B evidence changed; no inference made')
    files=['backend/markdown_section_check.py','backend/app/agent.py','backend/app/essays.py','backend/app/writing.py','agent/essay.ts','agent/essay_format.ts','agent/skills/ship30/SKILL.md','agent/skills/ship30/config.json']
    expected={p:sha256(subprocess.run(['git','show','4323911:'+p],capture_output=True,check=True).stdout).hexdigest() for p in files}
    baseline_trace=private_probe(BASELINE_PROBE,files)
    if expected!=baseline_trace['runtime_source_sha256']:raise RuntimeError('Running probe differs from committed 0.6B code; no inference made')
    private_config={p:sha256(Path(p).read_bytes()).hexdigest() for p in ['.env','compose.yaml']}
    with httpx.Client(trust_env=False,timeout=20) as client:
        before=client.get('http://127.0.0.1:8000/api/providers');before.raise_for_status();before=before.json()
        if before['model']!='qwen3:0.6b':raise RuntimeError('Chat model differs from required baseline')
        origin=client.get(f'http://127.0.0.1:8000/api/sessions/{ORIGIN_SID}/essays/{ORIGIN_RID}');origin.raise_for_status();origin=origin.json()
        response=client.get(f'http://127.0.0.1:8000/api/sessions/{ORIGIN_SID}/essays/{ORIGIN_RID}/sources');response.raise_for_status();sources={s['source_label']:s for s in response.json()}
        tags=client.get('http://127.0.0.1:11434/api/tags');tags.raise_for_status();tags=tags.json()['models']
        model=next((m for m in tags if m['name']=='qwen3:1.7b'),None)
        if not model or model.get('remote_model'):raise RuntimeError('Requested local 1.7B model not available')
        model_details={}
        for name in ['qwen3:0.6b','qwen3:1.7b']:
            show=client.post('http://127.0.0.1:11434/api/show',json={'model':name});show.raise_for_status();d=show.json()
            model_details[name]={'details':d.get('details'),'template_sha256':sha256(d.get('template','').encode()).hexdigest(),'parameters':d.get('parameters')}
    section=origin['outline']['sections'][1];labels=section['source_ids'];req=origin['request'];citation_text=', '.join('['+label+']' for label in labels)
    prompt=json.dumps({'topic':req['topic'],'audience':req['audience'],'constraints':req['constraints']},ensure_ascii=False)+f'\nUse the SAVED outline. Write ONLY section 2: '+section['heading']+'\nPurpose: '+section['purpose']+f'\nTarget210 words. Write body-only plain Markdown, no JSON, code fences, title, or repeated heading. The only valid citations are {citation_text}. Cite each factual paragraph with the exact supplied labels. Keep case-specific qualifications; no invented statistics, quotes, causal promises or anecdotes. Label any proposed user action Application:. Do not summarize or draft the remaining essay.'
    prompt+='\nWrite only plain Markdown for the requested section. No JSON or code fences. No tools are active. /no_think'
    prompt_hash=sha256(prompt.encode()).hexdigest()
    if not any(p['sha256']==prompt_hash for p in baseline_trace['user_prompts']):raise RuntimeError('Reconstructed prompt does not match actual 0.6B RPC prompt; no inference made')
    baseline_sources={s['source_label']:s for s in baseline['source_passages']}
    matches={label:sources[label]['chunk_id']==baseline_sources[label]['chunk_id'] and sha256(sources[label]['original_text'].encode()).hexdigest()==baseline_sources[label]['stored_text_sha256'] for label in labels}
    if not all(matches.values()):raise RuntimeError('Saved source packet changed; no inference made')
    folder=ROOT/('qwen17-section-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'));folder.mkdir(exist_ok=False)
    pre={'captured_at':datetime.now(timezone.utc).isoformat(),'prompt_sha256':prompt_hash,'prompt_matches_actual_baseline':True,'saved_outline_matches_baseline':origin['outline']==json.loads((ROOT/'live-20261106T111551/outline.json').read_text()),'source_matches_baseline':matches,'runtime_code_matches_commit':'4323911','baseline_trace':baseline_trace,'model_metadata':model,'model_details':model_details,'chat_provider_before':before,'baseline_preserved':True,'only_intended_inference_setting_change':'GENERATION_MODEL=qwen3:1.7b in the one Docker exec child, not the running API/Compose configuration','same_settings':{'context_window':4096,'max_output_tokens':850,'temperature':0,'thinking':'off','structured_grammar':False,'active_tools':[],'stage_deadline_seconds':90,'target_words':210},'warmup_inference':False,'comparison_limit':'One new first-load sample vs one earlier sample; baseline residency/host load not controlled. Download time excluded from stage latency.'}
    if not pre['saved_outline_matches_baseline']:raise RuntimeError('Saved outline changed; no inference made')
    (folder/'inputs.json').write_text(json.dumps(pre,indent=2)+'\n')
    command=[sys.executable,'scripts/docker.py','compose','exec','-T','-e','GENERATION_MODEL=qwen3:1.7b','api','python','-m','backend.markdown_section_check']
    execution=subprocess.run(command,capture_output=True,text=True,timeout=130)
    (folder/'command.json').write_text(json.dumps({'command':command,'exit_code':execution.returncode,'stderr':execution.stderr},indent=2)+'\n')
    if not execution.stdout.strip():raise RuntimeError('No result JSON; inspect saved command and private trace without retrying')
    result=json.loads(execution.stdout);(folder/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');(folder/'section.md').write_text(result['raw_markdown'])
    after_trace=private_probe(result['probe_run_id'],files)
    with httpx.Client(trust_env=False,timeout=20) as client:
        response=client.get('http://127.0.0.1:8000/api/providers');response.raise_for_status();after=response.json()
        response=client.get('http://127.0.0.1:11434/api/ps');response.raise_for_status();loaded=response.json()
    unchanged=all(sha256(Path(p).read_bytes()).hexdigest()==h for p,h in private_config.items())
    request_before=next(d for d in baseline_trace['diagnostics'] if d.get('event')=='provider_request')
    request_after=next((d for d in after_trace['diagnostics'] if d.get('event')=='provider_request'),{})
    verification={'captured_at':datetime.now(timezone.utc).isoformat(),'actual_prompt_identical':after_trace['user_prompts']==baseline_trace['user_prompts'],'same_prompt_bytes':request_after.get('prompt_bytes')==request_before.get('prompt_bytes'),'same_output_budget':request_after.get('max_tokens')==request_before.get('max_tokens'),'same_source_passage_ids_and_hashes':all(matches.values()) and result['source_passages']==baseline['source_passages'],'same_code':after_trace['runtime_source_sha256']==expected,'grammar_disabled':request_after.get('structured_grammar') is False,'provider_request_count':sum(d.get('event')=='provider_request' for d in after_trace['diagnostics']),'chat_model_after':after['model'],'chat_provider_unchanged':after==before,'env_and_compose_unchanged':unchanged,'baseline_output_review_unchanged':all(sha256(Path(p).read_bytes()).hexdigest()==h for p,h in preserve.items()),'new_trace':after_trace,'loaded_models_after':loaded,'manual_section_review':'pending; no automatic retry/full essay is permitted'}
    (folder/'comparison-verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    print(json.dumps({'evidence_directory':str(folder),'model':result['model'],'word_count':result['word_count'],'target_words':210,'elapsed_seconds':result['elapsed_seconds'],'automatic_section_checks_passed':result['automatic_section_checks_passed'],'checks':result['checks'],'failure':result['failure'],'input_comparison':{k:v for k,v in verification.items() if k not in {'new_trace','loaded_models_after'}},'section':result['raw_markdown']},ensure_ascii=False),flush=True)
    if execution.returncode:raise SystemExit(execution.returncode)


if __name__=='__main__':main()
