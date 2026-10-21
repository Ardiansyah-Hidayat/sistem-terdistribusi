import argparse
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Response, status
from fastapi.middleware.cors import CORSMiddleware

# Import configuration and storage service
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import STORAGE_NODES, STORAGE_BASE_DIR
from node.storage_service import StorageService

# Parse node arguments if running via CLI
parser = argparse.ArgumentParser(description="Distributed Storage Node Process")
parser.add_argument("--node-id", type=str, default="node1", help="Node identifier (node1, node2, node3)")
parser.add_argument("--port", type=int, default=8001, help="Port to run the node on")

args, unknown = parser.parse_known_args()

NODE_ID = args.node_id
PORT = args.port
NODE_CONFIG = STORAGE_NODES.get(NODE_ID, {
    "id": NODE_ID,
    "name": f"Storage Node ({NODE_ID})",
    "port": PORT,
    "dir": STORAGE_BASE_DIR / NODE_ID
})

storage_service = StorageService(node_id=NODE_ID, storage_dir=NODE_CONFIG["dir"])

app = FastAPI(
    title=f"Storage Node Service - {NODE_ID}",
    description=f"Storage Node API running on port {PORT}",
    version="1.0.0"
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Heartbeat endpoint for Coordinator health monitoring."""
    stats = storage_service.get_stats()
    return {
        "status": "online",
        "node_id": NODE_ID,
        "port": PORT,
        "file_count": stats["file_count"],
        "total_size_bytes": stats["total_size_bytes"]
    }

@app.post("/store/{file_id}")
async def store_file(file_id: str, file: UploadFile = File(...)):
    """Save binary file payload to local storage directory."""
    try:
        content = await file.read()
        result = storage_service.save_file(file_id=file_id, content=content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store file on {NODE_ID}: {str(e)}")

@app.get("/retrieve/{file_id}")
def retrieve_file(file_id: str):
    """Retrieve binary file from local storage."""
    try:
        content = storage_service.read_file(file_id=file_id)
        return Response(content=content, media_type="application/octet-stream")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{file_id}' not found on node {NODE_ID}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/{file_id}")
def delete_file(file_id: str):
    """Delete binary file from local storage."""
    deleted = storage_service.delete_file(file_id=file_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"File '{file_id}' not found on node {NODE_ID}")
    return {"status": "deleted", "node_id": NODE_ID, "file_id": file_id}

@app.get("/stats")
def get_stats():
    """Return storage metrics and file listing for this node."""
    return storage_service.get_stats()
