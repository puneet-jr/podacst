"""Export a named private revision without Git history or historical payloads.

No Git mutation, network, inference or publication. Evidence is projected, never
presented as a complete conversation export. Original files remain untouched.
"""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from datetime import datetime,timezone
SAFE_KEYS=set('id run_id session_id message_id user_message_id assistant_message_id client_message_id chunk_id source_label source_id label source_path source_hash sha256 hash corpus_revision revision release_revision baseline_revision provider selected model essay_model embedding_model tool name mode retrieval_mode status code error_code error_type type format scope captured_at started_at ended_at timestamp created_at completed_at updated_at date pi_session_id context_method workflow provenance version browser'.split())
SAFE_VALUES={'passed','failed','pending','blocked','verified','unverified','completed','ready','needs_review','insufficient_evidence','cancelled','running','pass','fail','skip','0/5','4/5'}

def digest(data):return hashlib.sha256(data).hexdigest()
def project(v,key=''):
 if isinstance(v,dict):return {k:project(x,k) for k,x in v.items()}
 if isinstance(v,list):return [project(x,key) for x in v]
 if not isinstance(v,str):return v
 if (key in SAFE_KEYS and len(v)<=240 and not any(x in v.lower() for x in ['bearer ','authorization','sk-or-'])) or v in SAFE_VALUES:return v
 return {'omitted_string_sha256':digest(v.encode()),'characters':len(v)}

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--revision',required=True);p.add_argument('--output',required=True);a=p.parse_args();src=Path(a.source);out=Path(a.output)
 revision=subprocess.check_output(['git','-C',str(src),'rev-parse',a.revision+'^{commit}'],text=True).strip()
 if out.exists():raise SystemExit('Refuse to overwrite an existing publication export')
 out.mkdir(parents=True);changes=[];originals={};files=subprocess.check_output(['git','-C',str(src),'ls-tree','-r','--name-only',revision],text=True).splitlines()
 for name in files:
  path=Path(name)
  if any(x in {'.git','.cache','node_modules','corpus','models','dist','__pycache__'} or x.startswith('.venv') for x in path.parts) or path.name.startswith('.env') and path.name!='.env.example' or path.suffix in {'.pdf','.gguf','.pyc','.pem','.key'}:changes.append({'path':name,'action':'excluded','reason':'private/generated/dependency path'});continue
  data=subprocess.check_output(['git','-C',str(src),'show',revision+':'+name]);originals[name]=digest(data);dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True)
  if name.startswith('docs/agent-transcripts/'):
   # The UI regression reads this reviewed artifact as a labelled rendering fixture.
   if name=='docs/agent-transcripts/phase-07/live-20261106T212600/accepted.json':
    v=json.loads(data);v={k:v[k] for k in ['id','session_id','user_message_id','assistant_message_id','status','request','context_message_ids','outline','sections','draft_md','validation','review','error_code']};original=json.loads(data);v['metadata']={k:original['metadata'][k] for k in ['fact_sections','advice_edits','evidence_edits'] if k in original['metadata']};v['metadata'].update({k:[{field:edit[field] for field in ['section','editor'] if field in edit} for edit in original['metadata'].get(k,[])] for k in ['advice_edits','evidence_edits']});v['metadata'].update(workflow='reviewed_fixture',model='historical reviewed artifact; not fresh inference',publication_note='Final reviewed essay and curated approved facts retained for deterministic UI regression. Full passages, raw advice stages, prompts and private traces omitted.');data=(json.dumps(v,indent=2)+'\n').encode();action='minimal_reviewed_rendering_fixture'
   elif path.suffix in {'.json','.jsonl'}:
    try:
     if path.suffix=='.json':v=project(json.loads(data));data=(json.dumps(v,indent=2)+'\n').encode()
     else:data=(''.join(json.dumps(project(json.loads(line)))+'\n' for line in data.decode().splitlines() if line.strip())).encode()
     action='metadata_projection'
    except (ValueError,UnicodeDecodeError):data=(json.dumps({'original_sha256':originals[name],'publication_omission':'Unparsed historical stream; private original preserved.'})+'\n').encode();action='unparsed_stream_omitted'
   elif path.suffix=='.md' and (path.name in {'README.md','PUBLICATION.md','report.md','diagnosis.md','command-ledger.md','phase-00-summary.md','qwen17-comparison-report.md'}):action='reviewed_narrative_retained'
   else:data=('# Private historical output omitted\n\nOriginal SHA-256: `'+originals[name]+'`.\n\nThe original remains private. See the phase report for measured results and failures; this placeholder is not a model output or conversation export.\n').encode();action='historical_payload_omitted'
   changes.append({'path':name,'action':action,'original_sha256':originals[name]})
  dest.write_bytes(data)
  mode=subprocess.check_output(['git','-C',str(src),'ls-tree',revision,'--',name],text=True).split()[0]
  if mode=='100755':dest.chmod(0o755)
 manifest={'prepared_at':datetime.now(timezone.utc).isoformat(),'base_revision':revision,'export_has_git_history':False,'published':False,'source_tracked_files':len(files),'runtime_changes':0,'evidence_policy':'Historical evidence is metadata-only projection or labelled narrative; raw provider/protocol/transcript payloads remain private. One minimal reviewed essay fixture is retained for UI tests, distinct from live generation.','changes':changes,'original_file_sha256':originals}
 (out/'docs/publication-selection.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'base_revision':revision,'tree':str(out),'tracked_files':len(files),'evidence_files_reviewed':len(changes),'runtime_changes':0,'git_history_included':False}))
if __name__=='__main__':main()
