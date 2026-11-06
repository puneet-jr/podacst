"""Organize the saved snapshot into seven honest phase commits with actual Git dates."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from publication_review import review


def run(*args,check=True,env=None):return subprocess.run(args,capture_output=True,text=True,check=check,env=env)


def group(path):
    p=Path(path)
    if path in {'.gitignore','LENNY_BUILD_FLOW.md','LENNY_CODEX_PROMPTS.md','docs/PRD.md','docs/scenarios.md','docs/assessment-audit.md','docs/phase-00-report.md'} or path.startswith('docs/agent-transcripts/phase-00'):return 1
    if path.startswith('spike/') or path=='docs/phase-01-report.md' or path.startswith('docs/agent-transcripts/phase-01/'):return 2
    if path in {'.dockerignore','.env.example','compose.yaml','backend/__init__.py','backend/app/__init__.py','backend/app/config.py','backend/app/db.py','backend/requirements.in','backend/requirements.lock','backend/alembic.ini','backend/migrate.py','backend/migrations/env.py','backend/migrations/versions/0001_foundation.py','backend/tests/__init__.py','backend/tests/test_api.py','backend/tests/test_unit.py','backend/tests/fake_rpc.py','backend/agent_smoke.py','agent/package.json','agent/package-lock.json','agent/fixture.json','agent/retrieval.ts','frontend/package.json','frontend/package-lock.json','frontend/tsconfig.json','frontend/index.html','frontend/Dockerfile','scripts/bootstrap.py','scripts/docker.py','scripts/capture.py','scripts/verify_phase2.py','docs/phase-02-report.md','docs/phase-02-operations.md'} or path.startswith('docs/agent-transcripts/phase-02/'):return 3
    if path in {'backend/app/transcripts.py','backend/app/embedding.py','backend/app/snapshot.py','backend/app/ingestion.py','backend/ingest.py','backend/ingestion_check.py','backend/migrations/versions/0002_ingestion.py','backend/tests/test_transcripts.py','backend/tests/test_embedding.py','scripts/fetch_corpus.py','scripts/verify_corpus_smoke.py','scripts/review_phase3.py','scripts/capture_phase3.py','docs/scenario-inputs.json','docs/phase-03-report.md','docs/phase-03-operations.md'} or path.startswith('docs/agent-transcripts/phase-03/'):return 4
    if path.startswith('eval/') or path in {'backend/app/retrieval.py','backend/evaluate_retrieval.py','backend/tests/test_retrieval.py','backend/tests/test_retrieval_db.py','scripts/verify_phase4.py','scripts/review_phase4.py','scripts/capture_phase4.py','docs/phase-04-report.md','docs/phase-04-operations.md'} or path.startswith('docs/agent-transcripts/phase-04/'):return 5
    if path in {'agent/conversation.ts','agent/conversation_policy.ts','agent/test_conversation_policy.ts','backend/conversation_check.py','backend/tests/test_conversation.py','backend/tests/test_conversation_db.py','backend/migrations/versions/0003_conversation.py','scripts/live_phase5.py','scripts/lifecycle_phase5.py','scripts/reopen_phase5.py','scripts/inspect_phase5.py','scripts/review_phase5.py','scripts/finalize_phase5.py','scripts/capture_phase5.py','docs/phase-05-report.md','docs/phase-05-operations.md'} or path.startswith('docs/agent-transcripts/phase-05/'):return 6
    return 7


MESSAGES={
1:('docs: record discovery, current PRD, and acceptance scenarios','Retrospective snapshot organization, not a historical initial release. The saved PRD/scenario documents include later updates; earlier versions are unavailable. Existing report times are evidence timestamps; this commit uses the actual current Git date.'),
2:('feat: preserve the Pi and local Ollama integration spike','Add the preserved controlled-tool spike, dependency locks, protocol tests and actual local failure/success evidence. Public evidence is sanitized; private originals remain excluded.'),
3:('infra: add Compose and PostgreSQL foundation','Add foundation schemas, current Compose/dependency configuration, startup tooling and PostgreSQL persistence evidence. Compose contains later corpus/trace mounts from the current saved version; shared runtime integration is grouped in the final snapshot commit.'),
4:('feat: add versioned transcript ingestion and local embeddings','Add exact-source parsing/chunking, local embedding identity, immutable refresh/migrations and integrity checks. Downloaded corpus and generated dependencies are excluded.'),
5:('feat: add retrieval and measured baseline evaluation','Add sparse/dense/hybrid retrieval, frozen cases/configuration and actual evaluation evidence. Scope remains nine episodes/373 passages; the broader quality target remains unmet.'),
6:('feat: add grounded chat tools and recovery evidence','Add controlled chat tools, citation/persistence contracts and actual local source/recovery evidence. The current shared conversation service has later essay-concurrency changes and is intentionally grouped in the final commit rather than reconstructed.'),
7:('wip: integrate current runtime and record blocked Phase 6 essays','Group current shared backend/frontend/runtime files whose earlier versions are unavailable, plus the dedicated essay workflow and actual failed local tests. Eighty-one contracts passed; corrected local essay run failed before section1 with an Ollama grammar error. No essay or Phase7 success is claimed. Include publication provenance, redactions and staged-file review.'),
}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--commit',action='store_true');args=parser.parse_args()
    paths=run('git','ls-files','--others','--exclude-standard','-z').stdout.split('\0');paths=sorted(p for p in paths if p)
    groups={n:[p for p in paths if group(p)==n] for n in range(1,8)}
    plan={'created_at':datetime.now(timezone.utc).isoformat(),'meaning':'Retrospective phase organization of saved current files; no backdated or invented earlier shared-file versions.','groups':[{'order':n,'title':MESSAGES[n][0],'files':groups[n]} for n in groups]}
    Path('.cache/publication-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps({'groups':[{'order':n,'title':MESSAGES[n][0],'file_count':len(groups[n])} for n in groups]},indent=2),flush=True)
    if not args.commit:return
    if run('git','rev-parse','--verify','HEAD',check=False).returncode==0:raise RuntimeError('Expected unborn branch; inspect existing commits before retrying.')
    if run('git','diff','--cached','--name-only').stdout.strip():raise RuntimeError('Expected an empty index before explicit group staging.')
    candidate=review(False)
    if not candidate['passed']:raise RuntimeError('Candidate review failed; no commits made.')
    review_dir=Path('.cache/staged-publication-reviews');review_dir.mkdir(exist_ok=True)
    results=[]
    # Remove any inherited date overrides. Git records real current author/committer dates.
    env={k:v for k,v in os.environ.items() if k not in {'GIT_AUTHOR_DATE','GIT_COMMITTER_DATE','GIT_AUTHOR_NAME','GIT_AUTHOR_EMAIL','GIT_COMMITTER_NAME','GIT_COMMITTER_EMAIL'}}
    for n,files in groups.items():
        if not files:raise RuntimeError('Unexpected empty phase group')
        run('git','add','--',*files)
        staged=review(True);(review_dir/(str(n)+'.json')).write_text(json.dumps(staged,indent=2)+'\n')
        if not staged['passed']:raise RuntimeError('Staged blob review failed; commit withheld.')
        actual=run('git','diff','--cached','--name-only','-z').stdout.split('\0');actual=sorted(p for p in actual if p)
        if actual!=files:raise RuntimeError('Staged paths differ from explicit reviewed phase plan')
        message=MESSAGES[n][0]+'\n\n'+MESSAGES[n][1]+'\n\n'+f"Staged review: {staged['file_count']} Git blobs; zero configured-secret, credential-pattern, excluded-path or source-payload findings. Reviewed at {staged['reviewed_at']}.\n"
        message_file=Path('.cache')/('publication-commit-'+str(n)+'.txt');message_file.write_text(message)
        run('git','commit','--file',str(message_file),env=env)
        value=run('git','log','-1','--format=%H%x09%aI%x09%cI%x09%s').stdout.strip().split('\t',3)
        record={'order':n,'commit':value[0],'author_time':value[1],'committer_time':value[2],'subject':value[3],'reviewed_files':len(files),'staged_review_passed':True};results.append(record)
        print(json.dumps(record),flush=True)
    Path('.cache/publication-commits.json').write_text(json.dumps(results,indent=2)+'\n')
    if run('git','status','--porcelain').stdout.strip():raise RuntimeError('Unexpected remaining nonignored changes; inspect before pushing.')


if __name__=='__main__':main()
