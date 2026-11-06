"""Create documented public evidence copies, retaining hash-identical originals privately.

No credentials are printed. Full transcript payloads are omitted; limited selected
answer quotes remain as attributed runtime evidence. This is a publication export,
not a new inference/test run, and does not rewrite historical outcomes.
"""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil

ROOT=Path('docs/agent-transcripts')
BACKUP=Path('.cache/publication-originals')
MANIFEST=Path('docs/publication-redactions.json')


def main():
    if MANIFEST.exists():raise SystemExit('Publication export already exists; inspect rather than overwrite it.')
    BACKUP.mkdir(parents=True,exist_ok=True);BACKUP.chmod(0o700)
    changes=[];counts={'omitted_transcript_fields':0,'redacted_home_paths':0}
    home=str(Path.home())
    def sanitize(value,path=()):
        if isinstance(value,dict):
            out={}
            for key,v in value.items():
                full_source=key in {'original_text','evidence_text'} or key=='text' and 'passages' in path and isinstance(v,str) and len(v)>600
                if full_source and isinstance(v,str) and v:
                    out[key]='[Full transcript payload omitted from public export; private original retained.]'
                    out[key+'_public_redaction']={'sha256':sha256(v.encode()).hexdigest(),'characters':len(v),'reason':'Full source passage payload; exact IDs, offsets, source hashes and limited selected answer quotes are retained.'}
                    counts['omitted_transcript_fields']+=1
                else:out[key]=sanitize(v,path+(str(key),))
            return out
        if isinstance(value,list):return [sanitize(v,path+('[]',)) for v in value]
        if isinstance(value,str):
            stripped=value.strip()
            if stripped.startswith(('{','[')):
                try:
                    parsed=json.loads(stripped);new=sanitize(parsed,path+('embedded_json',))
                    if new!=parsed:return json.dumps(new,ensure_ascii=False)
                except (ValueError,RecursionError):pass
            if '\n' in value:
                lines=value.splitlines(keepends=True);out=[];changed=False
                for line in lines:
                    part=line.strip()
                    if part.startswith(('{','[')):
                        try:
                            parsed=json.loads(part);new=sanitize(parsed,path+('embedded_jsonl',))
                            if new!=parsed:
                                out.append(json.dumps(new,ensure_ascii=False)+('\n' if line.endswith('\n') else ''));changed=True;continue
                        except (ValueError,RecursionError):pass
                    out.append(line)
                if changed:value=''.join(out)
            if home in value:counts['redacted_home_paths']+=value.count(home);value=value.replace(home,'$USER_HOME')
            return value
        return value
    originals=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        data=p.read_bytes();backup=BACKUP/p;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
        before=sha256(data).hexdigest();originals.append({'path':str(p),'sha256':before,'bytes':len(data)})
        if sha256(backup.read_bytes()).hexdigest()!=before:raise RuntimeError('Private backup integrity failure')
        if p.suffix=='.json':
            obj=json.loads(data);new=sanitize(obj);encoded=(json.dumps(new,indent=2,ensure_ascii=False)+'\n').encode() if new!=obj else data
        elif p.suffix=='.jsonl':
            lines=[];changed=False
            for line in data.decode().splitlines():
                obj=json.loads(line);new=sanitize(obj);changed|=new!=obj;lines.append(json.dumps(new,ensure_ascii=False))
            encoded=('\n'.join(lines)+'\n').encode() if changed else data
        else:
            decoded=data.decode();new=decoded.replace(home,'$USER_HOME');encoded=new.encode()
        if encoded!=data:
            p.write_bytes(encoded);changes.append({'path':str(p),'private_original_sha256':before,'public_export_sha256':sha256(encoded).hexdigest()})
    report={'exported_at':datetime.now(timezone.utc).isoformat(),'kind':'publication_sanitization_not_a_test_or_historical_reconstruction','private_backup':'.cache/publication-originals (ignored; parent0700)','private_original_file_count':len(originals),'private_originals':originals,'changed_public_files':changes,'counts':counts,'rules':['Omit full original_text/evidence_text source payloads and long passage.text fields, including nested command JSON/JSONL.','Retain source IDs, offsets/hashes, actual outcomes, timings and limited selected answer quotes.','Replace personal home paths in public runtime evidence.','Raw originals remain hash-identical in ignored private backup; historical check flags refer to those originals, not redacted placeholders.','Secrets are reviewed independently against the Git index before committing/pushing.']}
    MANIFEST.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'private_originals_preserved':len(originals),'public_files_changed':len(changes),'counts':counts}))


if __name__=='__main__':main()
