"""Run the app and share it on the internet via ngrok:  python .ngrok/start.py

Uses the `ngrok` Python package from requirements.txt, so no separate ngrok program is needed.
A free authtoken (https://dashboard.ngrok.com/get-started/your-authtoken) is read from
NGROK_AUTHTOKEN, then .ngrok/authtoken (save it once: python .ngrok/start.py --token <TOKEN>),
then the ngrok CLI config if you have one. Ctrl+C stops everything.
"""

import argparse
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import ngrok

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TOKEN_FILE = HERE / "authtoken"  # git-ignored
CLI_CONFIGS = [
    Path(os.environ.get("LOCALAPPDATA", "~")) / "ngrok" / "ngrok.yml",  # Windows
    Path.home() / "Library" / "Application Support" / "ngrok" / "ngrok.yml",  # macOS
    Path.home() / ".config" / "ngrok" / "ngrok.yml",  # Linux
]
TOKEN_IN_CONFIG = re.compile(r"^\s*authtoken:\s*['\"]?([\w-]+)", re.MULTILINE)
DEFAULT_PORT = 8501
PORT_ATTEMPTS = 20
STARTUP_SECONDS = 60
TOKEN_URL = "https://dashboard.ngrok.com/get-started/your-authtoken"
HINTS = {
    "ERR_NGROK_105": f"the authtoken is not valid. Copy it again from {TOKEN_URL} and run with --token <TOKEN>.",
    "ERR_NGROK_107": f"the authtoken was revoked. Get the current one from {TOKEN_URL} and run with --token <TOKEN>.",
    "ERR_NGROK_4018": f"an authtoken is required. Get it from {TOKEN_URL} and run with --token <TOKEN>.",
    "ERR_NGROK_108": "your account already has an ngrok session running (the free plan allows one). "
                     "Stop the other one: close its terminal, or run `taskkill /IM ngrok.exe /F` on Windows.",
    "ERR_NGROK_334": "your free ngrok address is already used by another running tunnel. Stop that one first.",
    "ERR_NGROK_15013": "you have no free dev domain yet. Claim it at https://dashboard.ngrok.com/domains.",
}


def find_token() -> str | None:
    """Authtoken from the environment, the saved file, or an ngrok CLI config."""
    if token := os.environ.get("NGROK_AUTHTOKEN"):
        return token.strip()
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip() or None
    for config in CLI_CONFIGS:
        if config.exists() and (found := TOKEN_IN_CONFIG.search(config.read_text(encoding="utf-8"))):
            return found.group(1)
    return None


def free_port(start: int) -> int:
    """First port from `start` that nothing is listening on (an old Streamlit may hold 8501)."""
    for port in range(start, start + PORT_ATTEMPTS):
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise SystemExit(f"No free port between {start} and {start + PORT_ATTEMPTS - 1}.")


def start_app(port: int) -> subprocess.Popen:
    """Launch Streamlit headless on `port` and wait until it answers its health check."""
    app = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", str(port),
         "--server.headless", "true"],
        cwd=ROOT, stdout=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + STARTUP_SECONDS
    while time.monotonic() < deadline and app.poll() is None:
        try:
            with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=2):
                return app
        except (URLError, OSError):
            time.sleep(0.5)
    app.terminate()
    raise SystemExit("Streamlit did not start; run `streamlit run app.py` to see the error.")


def open_tunnel(port: int, token: str) -> str:
    """Public https URL forwarding to the local app, or exit with a hint for known ngrok errors."""
    try:
        return ngrok.forward(port, authtoken=token).url()
    except ValueError as err:
        code = err.args[-1] if err.args else ""
        raise SystemExit(f"ngrok: {HINTS.get(code, ' '.join(map(str, err.args)))}") from None


def main() -> int:
    """Save the token if given, start the app on a free port, publish it, wait for Ctrl+C."""
    parser = argparse.ArgumentParser(description="Run Country Matcher with a public ngrok URL.")
    parser.add_argument("--token", help="ngrok authtoken; saved to .ngrok/authtoken for next time")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="preferred local port")
    args = parser.parse_args()
    if args.token:
        TOKEN_FILE.write_text(args.token.strip(), encoding="utf-8")
    token = find_token()
    if token is None:
        raise SystemExit(f"No ngrok authtoken. Get a free one at {TOKEN_URL}, then run:\n"
                         "  python .ngrok/start.py --token <TOKEN>")
    port = free_port(args.port)
    app = start_app(port)
    try:
        url = open_tunnel(port, token)
        print(f"\nPublic URL: {url}\nLocal URL:  http://localhost:{port}\nPress Ctrl+C to stop.\n", flush=True)
        app.wait()
        return app.returncode
    except KeyboardInterrupt:
        return 0
    finally:
        ngrok.kill()
        app.terminate()


if __name__ == "__main__":
    sys.exit(main())
