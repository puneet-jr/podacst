"""Create a fresh test DB on the isolated Compose server; never drop/reset databases."""
import os
import subprocess
import sys
from uuid import uuid4
from sqlalchemy import text
from backend.app.config import load_settings
from backend.app.db import make_engine


def main():
    settings=load_settings()
    if settings.db_host!='db':
        raise SystemExit('Contract checks require the isolated Compose db service')
    engine=make_engine(settings)
    database='lenny_contract_'+uuid4().hex[:12]
    with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as connection:
        connection.execute(text('CREATE DATABASE '+database))
    engine.dispose()
    print('Created new isolated contract database:',database,flush=True)
    env={**os.environ,'POSTGRES_DB':database}
    subprocess.run([sys.executable,'-m','backend.migrate'],env=env,check=True)
    subprocess.run([sys.executable,'-m','unittest','backend.tests.test_unit','backend.tests.test_transcripts','backend.tests.test_embedding','backend.tests.test_retrieval','backend.tests.test_conversation','backend.tests.test_writing','backend.tests.test_writing_rpc','backend.tests.test_api','backend.tests.test_retrieval_db','backend.tests.test_conversation_db','backend.tests.test_essays_db','-v'],env=env,check=True)
    print('Contract database retained; no database or volume was deleted.',flush=True)


if __name__=='__main__': main()
