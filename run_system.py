import sys
import subprocess
import time
import signal
import os
from pathlib import Path

# Force UTF-8 encoding for stdout/stderr in Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from config import COORDINATOR_HOST, COORDINATOR_PORT, LOCAL_IP, LAN_COORDINATOR_URL

processes = []

def signal_handler(sig, frame):
    print("\n[System Launcher] Shutting down all distributed nodes...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            proc.kill()
    print("[System Launcher] All processes terminated safely.")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 70)
    print("DISTRIBUTED FILE STORAGE SYSTEM - LOCALHOST & LAN NAS LAUNCHER")
    print("=" * 70)

    processes.clear()

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    from config import STORAGE_NODES

    for node_id, conf in STORAGE_NODES.items():
        node_host = conf.get("host", "127.0.0.1")
        node_port = conf.get("port", 8001)
        node_name = conf.get("name", node_id)
        if node_host in ("127.0.0.1", "localhost"):
            print(f"[Launcher] Starting {node_name} on http://127.0.0.1:{node_port} ...")
            proc = subprocess.Popen(
                [sys.executable, "-c", f"import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.argv=['main', '--node-id', '{node_id}', '--port', '{node_port}']; import uvicorn; from node.main import app; uvicorn.run(app, host='127.0.0.1', port={node_port}, log_level='warning')"],
                cwd=str(BASE_DIR),
                env=env
            )
            processes.append(proc)
        else:
            print(f"[Launcher] Detected {node_name} at external VM: {conf.get('url')}")


    time.sleep(1.5)

    # Launch Coordinator Server (Binds to 0.0.0.0:8000 for LAN Access)
    print(f"[Launcher] Starting Coordinator Server on 0.0.0.0:{COORDINATOR_PORT} ...")
    proc_coord = subprocess.Popen(
        [sys.executable, "-c", f"import sys; sys.stdout.reconfigure(encoding='utf-8'); import uvicorn; from coordinator.main import app; uvicorn.run(app, host='{COORDINATOR_HOST}', port={COORDINATOR_PORT}, log_level='info')"],
        cwd=str(BASE_DIR),
        env=env
    )
    processes.append(proc_coord)

    print("\n" + "=" * 70)
    print("✅ CLUSTER & NAS SERVER READY!")
    print(f"   💻 Laptop Local Access: http://127.0.0.1:{COORDINATOR_PORT}")
    print(f"   📱 Phone / LAN Access:  {LAN_COORDINATOR_URL}")
    print("=" * 70)
    print("Press Ctrl+C at any time to stop all processes.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
