import os
import sys
from pathlib import Path
import paramiko

VM_HOST = "192.168.56.102"
VM_PORT = 22
VM_USER = "vboxuser"
VM_PASS = "12345"

BASE_DIR = Path(__file__).resolve().parent

def run_vm_setup():
    print(f"[1/5] Connecting to VirtualBox VM at {VM_HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VM_HOST, port=VM_PORT, username=VM_USER, password=VM_PASS, timeout=10)
    print("   -> Connected successfully!")

    # Step 1: Install Python dependencies on VM
    print("[2/5] Installing FastAPI and Uvicorn on VM...")
    cmd_install = "pip install --break-system-packages fastapi uvicorn python-multipart"
    stdin, stdout, stderr = ssh.exec_command(cmd_install)
    out = stdout.read().decode()
    if out.strip():
        print("   -> " + out.splitlines()[-1])
    else:
        print("   -> Python packages ready.")

    # Step 2: Create project directories on VM
    print("[3/5] Setting up project folders on VM...")
    ssh.exec_command("mkdir -p ~/sistem_terdistribusi/node ~/sistem_terdistribusi/storage_data/node1")

    # Step 3: Transfer files via SFTP
    print("[4/5] Transferring node code to VM via SFTP...")
    sftp = ssh.open_sftp()
    
    # Upload node files
    sftp.put(str(BASE_DIR / "node" / "__init__.py"), "/home/vboxuser/sistem_terdistribusi/node/__init__.py")
    sftp.put(str(BASE_DIR / "node" / "main.py"), "/home/vboxuser/sistem_terdistribusi/node/main.py")
    sftp.put(str(BASE_DIR / "node" / "storage_service.py"), "/home/vboxuser/sistem_terdistribusi/node/storage_service.py")
    sftp.put(str(BASE_DIR / "config.py"), "/home/vboxuser/sistem_terdistribusi/config.py")
    sftp.close()
    print("   -> Files transferred successfully!")

    # Step 4: Add SSH Key for passwordless access
    pub_key_path = Path.home() / ".ssh" / "id_ed25519.pub"
    if pub_key_path.exists():
        pub_key = pub_key_path.read_text().strip()
        cmd_key = f'mkdir -p ~/.ssh && grep -qxF "{pub_key}" ~/.ssh/authorized_keys 2>/dev/null || echo "{pub_key}" >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys'
        ssh.exec_command(cmd_key)
        print("   -> Windows SSH key registered on VM!")

    # Step 5: Test starting the node in background
    print("[5/5] Launching Storage Node 1 on VM...")
    ssh.exec_command("fuser -k 8001/tcp")
    
    run_cmd = "nohup python3 -c \"import sys; sys.argv=['main', '--node-id', 'node1', '--port', '8001']; import uvicorn; from node.main import app; uvicorn.run(app, host='0.0.0.0', port=8001)\" > ~/sistem_terdistribusi/node.log 2>&1 &"
    ssh.exec_command(f"cd ~/sistem_terdistribusi && {run_cmd}")

    print("\n✅ Storage Node 1 is now running inside VirtualBox!")
    ssh.close()

if __name__ == "__main__":
    run_vm_setup()
