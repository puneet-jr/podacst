"""Use an isolated anonymous Docker CLI config; never read or change stored credentials."""
import json
import os
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
config = root / ".cache/docker-public"
config.mkdir(parents=True, exist_ok=True)
plugins = Path("/Applications/Docker.app/Contents/Resources/cli-plugins")
(config / "config.json").write_text(json.dumps({"auths": {}, "cliPluginsExtraDirs": [str(plugins)] if plugins.exists() else []}))
args = ["docker", "--config", str(config)]
socket = Path.home() / ".docker/run/docker.sock"
if socket.exists() and not os.environ.get("DOCKER_HOST"):
    args += ["--host", "unix://" + str(socket)]
os.chdir(root)
os.execvp("docker", [*args, *sys.argv[1:]])
