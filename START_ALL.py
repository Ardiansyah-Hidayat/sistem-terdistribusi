"""
START_ALL.py - One-click launcher for the entire Distributed Storage System
1. Resumes/starts the 3 VirtualBox VMs in headless background mode
2. Ensures node servers are running on all 3 VMs via SSH
3. Launches the Coordinator web server
4. Launches Ngrok tunnel
"""
import os
import sys
import subprocess
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

VBOX_MANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
VM_NAMES = ["storage-node-1", "storage-node-2", "storage-node-3"]

print("\n" + "=" * 60)
print("🚀 LAUNCHING DISTRIBUTED STORAGE SYSTEM...")
print("=" * 60)

# 1. Resume/Start the 3 VMs
if os.path.exists(VBOX_MANAGE):
    print("[*] Starting / Resuming VirtualBox VMs (headless mode)...")
    for vm in VM_NAMES:
        try:
            res = subprocess.run([VBOX_MANAGE, "startvm", vm, "--type", "headless"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                print(f"    [✓] {vm}: Running.")
            elif "already locked" in res.stderr.lower() or "already running" in res.stderr.lower():
                print(f"    [✓] {vm}: Already running.")
            else:
                print(f"    [i] {vm}: {res.stderr.strip() or 'OK'}")
        except Exception as e:
            print(f"    [-] VM {vm}: {e}")
    time.sleep(3)

# 2. Deploy nodes inside VMs
print("[*] Starting node processes in VMs...")
try:
    from deploy_vm_nodes import deploy_node, NODES
    for nid, info in NODES.items():
        deploy_node(nid, info["ip"], info["port"])
except Exception as e:
    print(f"    [-] Node deploy error: {e}")

# 3. Launch Coordinator in a new console window
print("[*] Launching Coordinator Server (port 8000)...")
subprocess.Popen(["cmd.exe", "/c", "start", "Coordinator Server", "python", "run_system.py"], shell=True)

# 4. Launch Ngrok in a new console window
print("[*] Launching Ngrok Tunnel...")
subprocess.Popen(["cmd.exe", "/c", "start", "Ngrok Tunnel", "python", "start_ngrok.py"], shell=True)

print("\n" + "=" * 60)
print("🎉 SYSTEM ONLINE & READY!")
print("=" * 60)
print("• Local Dashboard  : http://127.0.0.1:8000")
print("• Public Remote URL: https://carpentry-aloha-quotation.ngrok-free.dev")
print("=" * 60)
print("Ketik STOP_ALL.bat saat selesai untuk mematikan semua & melepas RAM!\n")
