import os
import re
import subprocess
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_cloudflared_exe() -> str:
    """Finds cloudflared executable in PATH or standard installation directories."""
    import shutil
    path_exe = shutil.which("cloudflared")
    if path_exe:
        return path_exe

    standard_paths = [
        r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
    ]
    for p in standard_paths:
        if os.path.exists(p):
            return p

    return "cloudflared"


def run_live_tunnel():
    """Starts FastAPI Uvicorn server and Cloudflare tunnel concurrently."""
    print("=========================================================")
    print("  🌐 LAUNCHING LIVE FASTAPI SERVER & CLOUDFLARE TUNNEL")
    print("=========================================================")

    python_exe = os.path.join(ROOT_DIR, "venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    cloudflared_cmd = find_cloudflared_exe()
    print(f"Using Cloudflare Tunnel CLI at: {cloudflared_cmd}")

    # 1. Start Uvicorn Server
    print("Starting FastAPI Uvicorn server at http://127.0.0.1:8000...")
    server_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "src.main:app", "--port", "8000", "--reload"],
        cwd=ROOT_DIR,
    )

    time.sleep(2)

    # 2. Launch Cloudflare Tunnel
    try:
        tunnel_proc = subprocess.Popen(
            [cloudflared_cmd, "tunnel", "--url", "http://127.0.0.1:8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        print("Launching Cloudflare Tunnel...")
        print("\n---------------------------------------------------------")
        print("  PASTE THIS WEBHOOK URL INTO YOUR GITHUB REPOSITORY:")
        print("---------------------------------------------------------")

        for line in tunnel_proc.stdout:
            if "trycloudflare.com" in line:
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if match:
                    url = match.group(0)
                    print(f"\n   👉 WEBHOOK PAYLOAD URL: {url}/webhook\n")
                    print("   - Content type: application/json")
                    print("   - Secret: (Value of GITHUB_WEBHOOK_SECRET in your .env)")
                    print("   - Events: Pull requests\n")
                    print("Press Ctrl+C to stop the live server and tunnel.\n")
                    break

        tunnel_proc.wait()
    except Exception as e:
        print(f"\n⚠️ Error launching Cloudflare Tunnel: {e}")
        server_proc.wait()


if __name__ == "__main__":
    run_live_tunnel()
