import argparse
from backend.app.config import load_settings
from backend.app.db import make_engine
from backend.app.ingestion import ingest, emit
from backend.app.snapshot import Snapshot
from sqlalchemy.exc import SQLAlchemyError


def main():
    parser=argparse.ArgumentParser(description='Pinned transcript ingestion; local Ollama only')
    parser.add_argument('--root',required=True)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--source-path',action='append',help='Select an exact manifest path; repeatable, complete manifest still controls deletion')
    parser.add_argument('--batch-size',type=int,default=4)
    parser.add_argument('--deadline-seconds',type=int,default=600)
    args=parser.parse_args()
    settings=load_settings();engine=make_engine(settings)
    try:
        snapshot=Snapshot.load(args.root)
        result=ingest(engine,settings,snapshot,limit=args.limit,source_paths=args.source_path,batch_size=args.batch_size,deadline_seconds=args.deadline_seconds)
        if result['status']=='failed':raise SystemExit(1)
    except SQLAlchemyError:
        emit('ingestion_cli_error',code='database_unavailable')
        raise SystemExit(1)
    except (ValueError,OSError,KeyError) as exc:
        emit('ingestion_cli_error',code=str(exc) if isinstance(exc,ValueError) else 'snapshot_unavailable')
        raise SystemExit(1)
    finally:engine.dispose()


if __name__=='__main__':main()
