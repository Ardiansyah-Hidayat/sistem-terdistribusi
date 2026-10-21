import os
import socket
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
STORAGE_BASE_DIR = BASE_DIR / "storage_data"
METADATA_FILE = STORAGE_BASE_DIR / "metadata.json"

# Function to detect local IPv4 address on LAN/Wi-Fi
def get_local_ip() -> str:
    """Retrieve the primary local IPv4 address of this laptop on the LAN."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a dummy address (doesn't send packets) to find active LAN interface
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

# Coordinator configuration
# 0.0.0.0 allows inbound connections from other devices on the LAN (e.g., phones)
COORDINATOR_HOST = "0.0.0.0"
COORDINATOR_PORT = 8000
LOCAL_IP = get_local_ip()
COORDINATOR_URL = f"http://127.0.0.1:{COORDINATOR_PORT}"
LAN_COORDINATOR_URL = f"http://{LOCAL_IP}:{COORDINATOR_PORT}"

# Cluster Deployment Mode:
# "local" : 3 node berjalan sebagai proses Python lokal di 127.0.0.1 (Port 8001, 8002, 8003). Tanpa butuh VirtualBox!
# "vm"    : 3 node berjalan di VirtualBox Ubuntu Server VM (192.168.56.102, .103, .104).
CLUSTER_MODE = os.environ.get("CLUSTER_MODE", "local").lower()

# Storage Nodes configuration
if CLUSTER_MODE == "vm":
    STORAGE_NODES = {
        "node1": {
            "id": "node1",
            "name": "Storage Node 1 (VirtualBox VM)",
            "host": "192.168.56.102",
            "port": 8001,
            "url": "http://192.168.56.102:8001",
            "dir": STORAGE_BASE_DIR / "node1"
        },
        "node2": {
            "id": "node2",
            "name": "Storage Node 2 (VirtualBox VM)",
            "host": "192.168.56.103",
            "port": 8002,
            "url": "http://192.168.56.103:8002",
            "dir": STORAGE_BASE_DIR / "node2"
        },
        "node3": {
            "id": "node3",
            "name": "Storage Node 3 (VirtualBox VM)",
            "host": "192.168.56.104",
            "port": 8003,
            "url": "http://192.168.56.104:8003",
            "dir": STORAGE_BASE_DIR / "node3"
        }
    }
else:
    STORAGE_NODES = {
        "node1": {
            "id": "node1",
            "name": "Storage Node 1 (Local)",
            "host": "127.0.0.1",
            "port": 8001,
            "url": "http://127.0.0.1:8001",
            "dir": STORAGE_BASE_DIR / "node1"
        },
        "node2": {
            "id": "node2",
            "name": "Storage Node 2 (Local)",
            "host": "127.0.0.1",
            "port": 8002,
            "url": "http://127.0.0.1:8002",
            "dir": STORAGE_BASE_DIR / "node2"
        },
        "node3": {
            "id": "node3",
            "name": "Storage Node 3 (Local)",
            "host": "127.0.0.1",
            "port": 8003,
            "url": "http://127.0.0.1:8003",
            "dir": STORAGE_BASE_DIR / "node3"
        }
    }


# Replication Policy
DEFAULT_REPLICATION_FACTOR = 2

# Health check settings
HEALTH_CHECK_INTERVAL = 3.0  # seconds between heartbeat checks
TIMEOUT_SECONDS = 4.0        # request timeout for nodes (prevents Wi-Fi latency false-alarms)
