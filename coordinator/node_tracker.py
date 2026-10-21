import asyncio
import httpx
import random
import paramiko
from typing import Dict, Any, List
from config import STORAGE_NODES, TIMEOUT_SECONDS

class NodeTracker:
    def __init__(self):
        self.nodes_config = STORAGE_NODES
        self.node_status: Dict[str, Dict[str, Any]] = {}

        # Initialize default state
        for node_id, config in self.nodes_config.items():
            self.node_status[node_id] = {
                "id": node_id,
                "name": config["name"],
                "port": config["port"],
                "url": config["url"],
                "status": "unknown",
                "file_count": 0,
                "total_size_bytes": 0,
                "error": None
            }

    async def toggle_node_process(self, node_id: str) -> bool:
        """
        Actually stop or start the real process inside the VirtualBox VM or local host!
        """
        if node_id not in self.nodes_config:
            return False

        config = self.nodes_config[node_id]
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 8001)
        
        # Check if currently online
        current_status = self.node_status.get(node_id, {}).get("status", "offline")
        is_online = (current_status == "online")

        if is_online:
            # STOP the real process on the VM
            if host not in ("127.0.0.1", "localhost"):
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(host, port=22, username="vboxuser", password="12345", timeout=3)
                    ssh.exec_command(f"fuser -k {port}/tcp; pkill -9 -f node.main")
                    ssh.close()
                except Exception as e:
                    print(f"[Remote Kill Error] {node_id} on {host}:{port} -> {e}")
            self.node_status[node_id]["status"] = "offline"
            self.node_status[node_id]["error"] = "Process Stopped"
            return False
        else:
            # START the real process on the VM
            if host not in ("127.0.0.1", "localhost"):
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(host, port=22, username="vboxuser", password="12345", timeout=3)
                    ssh.exec_command(f"mkdir -p ~/sistem_terdistribusi/storage_data/{node_id}")
                    start_script = f"nohup python3 -m uvicorn node.main:app --host 0.0.0.0 --port {port} > ~/sistem_terdistribusi/{node_id}.log 2>&1 &"
                    ssh.exec_command(f"cd ~/sistem_terdistribusi && {start_script}")
                    ssh.close()
                except Exception as e:
                    print(f"[Remote Start Error] {node_id} on {host}:{port} -> {e}")
            await asyncio.sleep(1.0)
            return True

    async def check_node_health(self, node_id: str, client: httpx.AsyncClient = None) -> Dict[str, Any]:
        """Ping a single storage node's /health endpoint."""
        config = self.nodes_config[node_id]
        url = f"{config['url']}/health"

        try:
            if client:
                res = await client.get(url)
            else:
                async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as c:
                    res = await c.get(url)

            if res.status_code == 200:
                data = res.json()
                self.node_status[node_id].update({
                    "status": "online",
                    "file_count": data.get("file_count", 0),
                    "total_size_bytes": data.get("total_size_bytes", 0),
                    "error": None
                })
            else:
                self.node_status[node_id].update({
                    "status": "offline",
                    "error": f"HTTP {res.status_code}"
                })
        except Exception as e:
            self.node_status[node_id].update({
                "status": "offline",
                "error": "Connection refused / offline"
            })
            
        return self.node_status[node_id]

    async def poll_all_nodes(self) -> Dict[str, Dict[str, Any]]:
        """Poll health status of all storage nodes concurrently using connection pooling."""
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            tasks = [self.check_node_health(node_id, client=client) for node_id in self.nodes_config]
            await asyncio.gather(*tasks)
        return self.node_status

    def get_online_nodes(self) -> List[str]:
        """Return list of online node IDs."""
        return [
            node_id for node_id, info in self.node_status.items()
            if info["status"] == "online"
        ]

    def select_replica_nodes(self, count: int = 2) -> List[str]:
        """
        Select 'count' online storage nodes for replication.
        Prioritizes nodes with fewer stored files.
        """
        online = self.get_online_nodes()
        if len(online) < count:
            return online
        
        sorted_nodes = sorted(
            online,
            key=lambda nid: self.node_status[nid].get("file_count", 0)
        )
        return sorted_nodes[:count]
