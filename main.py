import atexit
import os
import subprocess
from pathlib import Path
from typing import Optional

import dotenv
import psutil
import uvicorn

dotenv.load_dotenv()

HOT_RELOAD = os.environ.get("ENVIRONMENT", "prod") == "dev"


def fully_kill_process(process: Optional[subprocess.Popen]):
    if process is None:
        return
    for child_process in psutil.Process(process.pid).children(True):
        try:
            child_process.kill()
        except psutil.NoSuchProcess:
            pass
    process.kill()


def start_server():
    CF_PROCESS = None
    if os.environ.get("RUN_CLOUDFLARED") == "yes":
        cf_domain = os.environ.get("CLOUDFLARED_DOMAIN")
        if not Path("./cf_creds.json").exists():
            print("Retrieving cloudflare credentials...")
            subprocess.run(
                f"cloudflared tunnel token --cred-file cf_creds.json {cf_domain}",
                shell=True,
            )
        CF_PROCESS = subprocess.Popen(
            f"cloudflared tunnel run --cred-file cf_creds.json --url 0.0.0.0:8002 {cf_domain}",
            shell=True,
            start_new_session=True,
        )
    atexit.register(lambda: fully_kill_process(CF_PROCESS))

    uvicorn.run("src.api:app", host="0.0.0.0", port=8002, reload=HOT_RELOAD)


if __name__ == "__main__":
    start_server()
