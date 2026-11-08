"""Installed Pi cloud initialization only: no provider request, no real key."""
import asyncio,json,tempfile,argparse
from pathlib import Path
from pydantic import SecretStr
from backend.app.agent import PiRPC,ROOT
from backend.app.config import load_settings
async def main():
    parser=argparse.ArgumentParser();parser.add_argument('--provider',choices=['anthropic','openrouter'],default='anthropic');provider=parser.parse_args().provider
    settings=load_settings().model_copy(update={'default_provider':provider,'anthropic_api_key':SecretStr('synthetic-initialization-only') if provider=='anthropic' else SecretStr(''),'openrouter_api_key':SecretStr('synthetic-initialization-only') if provider=='openrouter' else SecretStr('')})
    with tempfile.TemporaryDirectory() as d:
        rpc=PiRPC(Path(d)/'trace',settings=settings,require_tool=False,tool_name='',extension=ROOT/'agent/application_advice.ts')
        try:
            state=await rpc.start()
            print(json.dumps({'provider':state['model']['provider'],'model':state['model']['id'],'base_url':state['model']['baseUrl'],'initial_message_count':state['messageCount'],'provider_requests':0,'synthetic_key':True,'proof':'Installed Pi can resolve the configured selected native provider model; NOT live cloud API validation.'}))
        finally:await rpc.close()
        assert rpc.process.returncode is not None
if __name__=='__main__':asyncio.run(main())
