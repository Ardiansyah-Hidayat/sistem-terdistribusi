"""
start_ngrok.py - Ngrok launcher for Distributed Storage Coordinator
Starts ngrok tunnel and syncs the public URL with the Web Dashboard.
"""
import subprocess
import time
import json
import urllib.request
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

NGROK_EXE = os.path.join(os.path.dirname(__file__), "ngrok.exe")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "ngrok_config.txt")
LOG_FILE = os.path.join(os.path.dirname(__file__), "ngrok.log")

# Read optional static domain if saved
default_domain = "carpentry-aloha-quotation.ngrok-free.dev"
domain_arg = [f"--url={default_domain}"]
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            domain = f.read().strip()
            if domain:
                domain_arg = [f"--url={domain}"]
    except Exception:
        pass

print("[*] Starting Ngrok tunnel for Coordinator (port 8000)...")

# Open log file for output so pipe buffer never deadlocks ngrok
log_f = open(LOG_FILE, "w", encoding="utf-8")

cmd = [NGROK_EXE, "http", "8000", "--log=stdout"] + domain_arg
process = subprocess.Popen(
    cmd,
    stdout=log_f,
    stderr=subprocess.STDOUT
)

# Wait up to 10 seconds for ngrok local API to become available
public_url = None
for _ in range(20):
    time.sleep(0.5)
    try:
        req = urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=2)
        data = json.loads(req.read().decode())
        tunnels = data.get("tunnels", [])
        for t in tunnels:
            url = t.get("public_url")
            if url and url.startswith("https://"):
                public_url = url
                break
            elif url and not public_url:
                public_url = url
        if public_url:
            break
    except Exception:
        pass

if public_url:
    # Save URL to file for easy access by coordinator dashboard
    url_file = os.path.join(os.path.dirname(__file__), "public_url.txt")
    with open(url_file, "w", encoding="utf-8") as f:
        f.write(public_url)

    print("\n" + "=" * 65)
    print("🚀 NGROK REMOTE ACCESS AKTIF! (Tetap & Permanen)")
    print("=" * 65)
    print(f"🔗 Public URL : {public_url}")
    print("=" * 65)
    print("📱 Kamu bisa copy link di atas dan buka di HP dari mana saja.")
    print("Tekan Ctrl+C untuk menghentikan tunnel.\n")
    sys.stdout.flush()

    try:
        while True:
            time.sleep(1)
            # Check if ngrok died unexpectedly
            if process.poll() is not None:
                print(f"[-] Ngrok process stopped with code {process.returncode}")
                break
    except KeyboardInterrupt:
        print("\n[*] Stopping ngrok...")
    finally:
        process.terminate()
        try:
            log_f.close()
        except Exception:
            pass
else:
    print("[-] Gagal mendeteksi URL Ngrok. Kemungkinan butuh authtoken.")
    print("[*] Log output dari Ngrok:")
    try:
        log_f.flush()
        log_f.close()
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading log: {e}")
    process.terminate()
