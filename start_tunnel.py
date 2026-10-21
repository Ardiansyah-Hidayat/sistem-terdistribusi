"""
start_tunnel.py - Cloudflare Tunnel launcher for Distributed File Storage System
Exposes local Coordinator (http://127.0.0.1:8000) securely to the internet.
"""
import subprocess
import re
import sys
import time
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

CLOUDFLARED_PATH = os.path.join(os.path.dirname(__file__), "cloudflared.exe")

if not os.path.exists(CLOUDFLARED_PATH):
    print("[-] Error: cloudflared.exe not found in current directory.")
    sys.exit(1)

print("[*] Starting Cloudflare Tunnel for Coordinator (port 8000)...")
print("[*] Connecting to Cloudflare global network...")

cmd = [CLOUDFLARED_PATH, "tunnel", "--url", "http://127.0.0.1:8000"]
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    encoding="utf-8",
    errors="replace"
)

tunnel_url = None
url_regex = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

# Read lines until we find the public URL
for line in process.stdout:
    match = url_regex.search(line)
    if match:
        tunnel_url = match.group(0)
        break

if tunnel_url:
    # Save URL to file for easy access
    url_file = os.path.join(os.path.dirname(__file__), "public_url.txt")
    with open(url_file, "w", encoding="utf-8") as f:
        f.write(tunnel_url)

    print("\n" + "=" * 65)
    print("🚀 REMOTE ACCESS AKTIF! (Bisa diakses dari mana saja)")
    print("=" * 65)
    print(f"🔗 Public URL : {tunnel_url}")
    print("=" * 65)
    print("📱 Kamu bisa copy link di atas dan buka di HP (pakai kuota/data).")
    print("Tekan Ctrl+C untuk menghentikan tunnel.\n")
    sys.stdout.flush()

    try:
        # Keep reading and printing log lines if any errors occur
        for line in process.stdout:
            pass
    except KeyboardInterrupt:
        print("\n[*] Stopping tunnel...")
        process.terminate()
else:
    print("[-] Gagal mendapatkan Public URL dari Cloudflare.")
    process.terminate()
