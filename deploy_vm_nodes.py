import sys
import paramiko
from pathlib import Path

NODES = {
    "node1": {"ip": "192.168.56.102", "port": 8001},
    "node2": {"ip": "192.168.56.103", "port": 8002},
    "node3": {"ip": "192.168.56.104", "port": 8003},
}

def deploy_node(node_id, ip, port):
    print(f"Deploying {node_id} to VM at {ip}:{port}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=22, username="vboxuser", password="12345", timeout=5)

        # Kill any existing process on target port
        ssh.exec_command(f"fuser -k {port}/tcp")
        
        # Ensure directory exists
        ssh.exec_command(f"mkdir -p ~/sistem_terdistribusi/storage_data/{node_id}")

        # Start storage node service
        runner = f"""nohup python3 -c "import sys; sys.argv=['main', '--node-id', '{node_id}', '--port', '{port}']; import uvicorn; from node.main import app; uvicorn.run(app, host='0.0.0.0', port={port})" > ~/sistem_terdistribusi/{node_id}.log 2>&1 &"""
        ssh.exec_command(f"cd ~/sistem_terdistribusi && {runner}")
        ssh.close()
        print(f"   -> {node_id} successfully launched on {ip}:{port}")
        return True
    except Exception as e:
        print(f"   -> Error on {node_id} ({ip}): {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 3:
        deploy_node(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    else:
        for nid, info in NODES.items():
            deploy_node(nid, info["ip"], info["port"])
