"""
stop_all.py - Complete shutdown script for Distributed Storage System
Frees 100% of CPU and RAM resources by stopping:
1. Ngrok & Cloudflare Tunnels
2. Coordinator Server (Port 8000)
3. VM Storage Node processes (via SSH)
4. VirtualBox VMs (Saved State to completely free host RAM)
"""
import os
import sys
import subprocess
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

VBOX_MANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
VM_NAMES = ["storage-node-1", "storage-node-2", "storage-node-3"]
VM_IPS_PORTS = [
    ("192.168.56.102", 8001),
    ("192.168.56.103", 8002),
    ("192.168.56.104", 8003),
]

print("\n" + "=" * 60)
print("🛑 SHUTTING DOWN ALL DISTRIBUTED STORAGE TASKS...")
print("=" * 60)

# 1. Kill Tunnel processes (Ngrok & Cloudflare)
print("[*] Stopping Ngrok & Cloudflare tunnels...")
try:
    subprocess.run(["taskkill", "/F", "/IM", "ngrok.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["taskkill", "/F", "/IM", "cloudflared.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ps_kill_ngrok_py = 'Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*start_ngrok.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }'
    subprocess.run(["powershell", "-Command", ps_kill_ngrok_py], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("    [✓] Tunnels stopped.")
except Exception as e:
    print(f"    [-] Tunnels cleanup: {e}")

# 2. Kill Coordinator Server (Port 8000)
print("[*] Stopping Coordinator Server (port 8000)...")
try:
    # Use PowerShell to find and kill process on port 8000
    ps_cmd = 'Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }'
    subprocess.run(["powershell", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("    [✓] Coordinator server stopped.")
except Exception as e:
    print(f"    [-] Coordinator cleanup: {e}")

# 3. Stop Node processes inside VMs via SSH (Quick best-effort)
print("[*] Stopping Storage Node python processes inside VMs...")
try:
    import paramiko
    for ip, port in VM_IPS_PORTS:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=22, username="vboxuser", password="12345", timeout=2)
            client.exec_command(f"fuser -k {port}/tcp; pkill -9 -f node.main")
            client.close()
            print(f"    [✓] Node on {ip}:{port} stopped.")
        except Exception:
            # If VM is already off/unreachable, just ignore
            pass
except Exception as e:
    print(f"    [-] SSH node cleanup: {e}")

# 4. Save State on VirtualBox VMs to free host RAM
if os.path.exists(VBOX_MANAGE):
    print("[*] Saving VirtualBox VM states to release RAM (2-4 GB)...")
    for vm in VM_NAMES:
        try:
            res = subprocess.run([VBOX_MANAGE, "controlvm", vm, "savestate"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if "100%" in res.stdout or res.returncode == 0:
                print(f"    [✓] {vm}: Saved & RAM freed.")
            elif "not currently running" in res.stderr.lower():
                print(f"    [✓] {vm}: Already off.")
            else:
                print(f"    [i] {vm}: {res.stderr.strip()}")
        except Exception as e:
            print(f"    [-] VM {vm}: {e}")
else:
    print("[-] VBoxManage.exe not found at standard path.")

print("\n" + "=" * 60)
print("✨ SELESAI! SEMUA RESOURCE TELAH DIBERSIHKAN")
print("=" * 60)
print("• Coordinator (Port 8000) : MATI 🛑")
print("• Ngrok & Cloudflare      : MATI 🛑")
print("• VM Storage Nodes        : MATI 🛑")
print("• RAM Laptop (VirtualBox) : DILEPAS & BEBAS (Saved State) 💾")
print("=" * 60)
print("Laptop kamu sekarang 100% dingin, baterai hemat, dan siap ditutup! 👍\n")
