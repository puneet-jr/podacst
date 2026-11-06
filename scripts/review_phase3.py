"""Read-only gate audit, with metadata-only reports; never prints credentials/source text."""
import ast
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT/'docs/agent-transcripts/phase-03'


def source_files():
    ignored = {'.git', '.cache', '.venv', '.venv-phase2', 'node_modules', 'dist', '__pycache__', '.agents', '.codex', '.aws'}
    files = []
    for folder, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ignored and not (Path(folder).name == 'docs' and d == 'agent-transcripts')]
        for name in names:
            if name.startswith('.env') and name != '.env.example': continue
            p = Path(folder)/name
            if p.is_file(): files.append(p)
    return sorted(files)


def main():
    checks = []
    def check(name, passed, detail):
        checks.append({'name': name, 'passed': bool(passed), 'detail': detail})
    rows = [json.loads(line) for line in (EVIDENCE/'commands.jsonl').read_text().splitlines()]
    tests = [r for r in rows if r['command'][-1:] == ['backend.contract_check']]
    check('Final contract suite on real PostgreSQL', bool(tests) and tests[-1]['exit_code'] == 0 and 'Ran 30 tests' in tests[-1]['stderr'] and '\nOK\n' in tests[-1]['stderr'], '30 tests: 23 unit/parser/mock and 7 DB/API; retained DB in command log')
    integrity = json.loads((EVIDENCE/'container-evidence/ingestion-integrity-lenny_ingest_49ebd8d3882f/result.json').read_text())
    check('Separate real local fixture integrity', integrity['passed'] and len(integrity['checks']) == 12 and all(r['passed'] for r in integrity['checks']), 'Actual PostgreSQL/Ollama; synthetic sources and labelled fault injection')
    smoke = [json.loads(line) for line in (EVIDENCE/'smoke-20261106T053920/results.jsonl').read_text().splitlines()]
    summary = next(r for r in smoke if r['kind'] == 'actual_smoke_summary')
    check('Real pinned corpus smoke and repeat', summary['passed'] and len(summary['checks']) == 7 and all(summary['checks'].values()), {'first_duration_seconds': summary['first']['duration_seconds'], 'repeat_duration_seconds': summary['repeat']['duration_seconds'], 'active_chunks': summary['proof']['active_chunks'], 'selected': summary['first']['selected'], 'discovered': summary['first']['discovered']})
    audit = json.loads((EVIDENCE/'corpus-audit.json').read_text())
    check('Full parser audit is distinct from embeddings', audit['parsed'] == audit['source_count'] and not audit['errors'] and audit['embedded_by_this_audit'] == 0, {'parsed': audit['parsed'], 'candidate_chunks': audit['candidate_chunks']})
    files = source_files()
    syntax_errors = []
    for p in files:
        if p.suffix == '.py':
            try: ast.parse(p.read_text())
            except SyntaxError: syntax_errors.append(str(p.relative_to(ROOT)))
    check('Current Python source parses', not syntax_errors, {'python_files': sum(p.suffix == '.py' for p in files), 'errors': syntax_errors})
    link_errors = []
    for p in files:
        if p.suffix != '.md' or p.name in {'LENNY_BUILD_FLOW.md', 'LENNY_CODEX_PROMPTS.md'}: continue
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            target = target.strip('<>').split('#')[0]
            if not target or '://' in target or target.startswith('mailto:'): continue
            if not (p.parent/target).exists(): link_errors.append({'file': str(p.relative_to(ROOT)), 'target': target})
    check('Current documentation links resolve', not link_errors, link_errors)
    ids = re.findall(r'^\| ((?:FD|API|AG|SES|DB|MOD|KB|RAG|ESS|ART|OPS|DEL)-\d{2}) \|', (ROOT/'docs/requirements.md').read_text(), re.M)
    check('All 29 requirement IDs present once', len(ids) == len(set(ids)) == 29, {'count': len(ids)})
    scenario_path = ROOT/'docs/scenario-inputs.json'
    scenarios = json.loads(scenario_path.read_text())
    corpus = ROOT/'.cache/corpus'/scenarios['corpus_revision']
    invalid_anchors = []
    for case in scenarios['scenarios']:
        raw = (corpus/case['source_path']).read_bytes()
        text = raw.decode()
        if sha256(raw).hexdigest() != case['source_sha256']: invalid_anchors.append(case['id'])
        for anchor in case['anchors']:
            if sha256(text[anchor['char_start']:anchor['char_end']].encode()).hexdigest() != anchor['passage_sha256']: invalid_anchors.append(case['id'])
    check('Five scenario inputs have reproducible source anchors', len(scenarios['scenarios']) == 5 and not invalid_anchors, {'invalid': invalid_anchors, 'freeze_sha256': sha256(scenario_path.read_bytes()).hexdigest(), 'outcomes': 'not run', 'duration_caps': 'pending complete-journey baseline'})
    preserved = json.loads((EVIDENCE/'preservation.json').read_text())
    old = json.loads((ROOT/'docs/agent-transcripts/phase-02/phase-01-preservation.json').read_text())['phase_01_evidence_current_hashes']
    check('Historical evidence preserved through final audit', not preserved['spike_changed'] and not preserved['phase_01_evidence_changed'] and all(sha256((ROOT/p).read_bytes()).hexdigest() == h for p,h in {**old, **preserved['phase_02_evidence_current_hashes']}.items()), {'phase_1_files': len(old), 'phase_2_files': len(preserved['phase_02_evidence_current_hashes']), 'original_spike_files': preserved['original_spike_files']})
    source_hash_rows = [r for r in rows if any('files=[p for base in' in part for part in r['command'])]
    installed = json.loads(source_hash_rows[-1]['stdout']) if source_hash_rows else {}
    mismatch = [p for p,h in installed.items() if sha256((ROOT/p).read_bytes()).hexdigest() != h]
    check('Tested container backend/agent matches workspace', bool(installed) and not mismatch, {'files': len(installed), 'mismatch': mismatch})
    secret = None
    for line in (ROOT/'.env').read_text().splitlines():
        if line.startswith('POSTGRES_PASSWORD='): secret = line.split('=',1)[1].strip().strip('"\'')
    suspects = [str(p.relative_to(ROOT)) for p in files if secret and secret.encode() in p.read_bytes()]
    for p in EVIDENCE.rglob('*'):
        if p.is_file() and secret and secret.encode() in p.read_bytes(): suspects.append(str(p.relative_to(ROOT)))
    check('Generated credential absent from source/evidence', bool(secret) and not suspects, {'suspect_paths': suspects, 'limit': 'Exact generated credential check; not a complete security audit'})
    json_errors = []
    for p in (ROOT/'docs/agent-transcripts').rglob('*'):
        if p.suffix not in {'.json', '.jsonl'}: continue
        try:
            if p.suffix == '.json': json.loads(p.read_text())
            else:
                for line in p.read_text().splitlines():
                    if line.strip(): json.loads(line)
        except (ValueError, UnicodeError): json_errors.append(str(p.relative_to(ROOT)))
    check('Saved JSON evidence parses', not json_errors, json_errors)
    forbidden = [str(p.relative_to(ROOT)) for p in files if p.suffix == '.pdf' or p.name.casefold() == 'transcript.md']
    check('No confidential PDF or full corpus in source list', not forbidden and '.cache' in (ROOT/'.dockerignore').read_text(), {'unexpected_paths': forbidden})
    for name, match, description in [('Frontend TypeScript/build', ['npm','--prefix','frontend','run','build'], 'TypeScript + Vite, no visual browser pass'), ('Installed dependency compatibility', ['python3','scripts/docker.py','compose','exec','-T','api','python','-m','pip','check'], 'Actual container pip check')]:
        evidence = [r for r in rows if r['command'] == match]
        check(name, bool(evidence) and evidence[-1]['exit_code'] == 0, description)
    images = [r for r in rows if r['command'][-3:] == ['images','--format','json']]
    manifest = {'created_at': datetime.now(timezone.utc).isoformat(), 'revision': 'No Git repository initialized; SHA-256 source identity for Phase 3. Runtime evidence is separate.', 'corpus_revision': scenarios['corpus_revision'], 'images': json.loads(images[-1]['stdout']) if images else [], 'files': [{'path':str(p.relative_to(ROOT)), 'sha256':sha256(p.read_bytes()).hexdigest()} for p in files]}
    (EVIDENCE/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    result = {'captured_at':datetime.now(timezone.utc).isoformat(), 'passed':all(c['passed'] for c in checks), 'checks':checks, 'limits':['3/303 corpus episodes indexed; full ingestion unverified','No retrieval ranking/semantic answer/essay/SC-01 outcomes','Browser bootstrap failed before connection; no UI inspection','Corpus redistribution rights/full coding-conversation export unresolved','No production authentication, cloud integration or clean evaluator rehearsal']}
    (EVIDENCE/'final-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not result['passed']: raise SystemExit(1)


if __name__ == '__main__': main()
