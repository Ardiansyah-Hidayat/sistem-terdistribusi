import asyncio
import sys
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Header, Query, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Add root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import METADATA_FILE, DEFAULT_REPLICATION_FACTOR, TIMEOUT_SECONDS, COORDINATOR_PORT, LOCAL_IP, LAN_COORDINATOR_URL
from coordinator.metadata_manager import MetadataManager
from coordinator.node_tracker import NodeTracker
from coordinator.auth_manager import AuthManager

metadata_mgr = MetadataManager(METADATA_FILE)
node_tracker = NodeTracker()
auth_mgr = AuthManager()

app = FastAPI(
    title="Distributed Storage System - Coordinator",
    description="Coordinator / Master Node Server managing metadata and storage node replication",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Models & Dependencies
class LoginRequest(BaseModel):
    role: str  # "admin" or "guest"
    username: Optional[str] = None
    password: Optional[str] = None

class GuestAccessRequest(BaseModel):
    enabled: bool

class GuestAuthorityRequest(BaseModel):
    enabled: bool

def get_token(x_auth_token: Optional[str] = Header(None), token: Optional[str] = Query(None)) -> Optional[str]:
    return x_auth_token or token

def require_session(token: Optional[str] = Depends(get_token)) -> dict:
    return auth_mgr.get_session(token)

def require_admin(token: Optional[str] = Depends(get_token)) -> dict:
    return auth_mgr.require_admin(token)

def require_admin_or_guest_authorized(token: Optional[str] = Depends(get_token)) -> dict:
    return auth_mgr.require_admin_or_guest_authorized(token)


@app.get("/api/system/info")
def get_system_info():
    """Return LAN access URL and system network information (Public)."""
    public_url = None
    pub_path = Path(__file__).resolve().parent.parent / "public_url.txt"
    if pub_path.exists():
        try:
            public_url = pub_path.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return {
        "local_ip": LOCAL_IP,
        "coordinator_port": COORDINATOR_PORT,
        "lan_url": LAN_COORDINATOR_URL,
        "local_url": f"http://127.0.0.1:{COORDINATOR_PORT}",
        "public_url": public_url,
        "guest_access_enabled": auth_mgr.guest_access_enabled,
        "guest_authority_enabled": auth_mgr.guest_authority_enabled,
        "replication_factor": DEFAULT_REPLICATION_FACTOR
    }


# Auth Endpoints
@app.post("/api/auth/login")
def auth_login(req: LoginRequest):
    if req.role == "admin":
        return auth_mgr.login_admin(req.username or "", req.password or "")
    elif req.role == "guest":
        return auth_mgr.login_guest()
    else:
        raise HTTPException(status_code=400, detail="Peran tidak valid")

@app.post("/api/auth/logout")
def auth_logout(token: Optional[str] = Depends(get_token)):
    if token:
        auth_mgr.logout(token)
    return {"status": "success", "message": "Berhasil logout"}

@app.get("/api/auth/status")
def auth_status():
    """Public endpoint to check if guest access and experiment authority are currently open."""
    return {
        "guest_access_enabled": auth_mgr.guest_access_enabled,
        "guest_authority_enabled": auth_mgr.guest_authority_enabled
    }

@app.get("/api/auth/me")
def auth_me(session: dict = Depends(require_session)):
    return {
        "status": "authenticated",
        "role": session.get("role"),
        "username": session.get("username"),
        "guest_access_enabled": auth_mgr.guest_access_enabled,
        "guest_authority_enabled": auth_mgr.guest_authority_enabled
    }

@app.post("/api/admin/guest-access")
def toggle_guest_access(req: GuestAccessRequest, admin: dict = Depends(require_admin)):
    status = auth_mgr.set_guest_access(req.enabled)
    return {
        "status": "success",
        "guest_access_enabled": status,
        "message": f"Akses Guest sekarang {'DIIZINKAN' if status else 'DIBLOKIR'}"
    }

@app.post("/api/admin/guest-authority")
def toggle_guest_authority(req: GuestAuthorityRequest, admin: dict = Depends(require_admin)):
    status = auth_mgr.set_guest_authority(req.enabled)
    return {
        "status": "success",
        "guest_authority_enabled": status,
        "message": f"Izin Eksperimen Guest sekarang {'DIBERIKAN (Guest bisa simulate failure & delete)' if status else 'DICABUT'}"
    }


# Background heartbeat task
async def heartbeat_loop():
    """Background task to continuously poll storage node health."""
    while True:
        try:
            await node_tracker.poll_all_nodes()
        except Exception as e:
            print(f"[Coordinator Heartbeat Error]: {e}")
        await asyncio.sleep(3.0)

@app.on_event("startup")
async def startup_event():
    # Perform initial health check immediately
    await node_tracker.poll_all_nodes()
    # Start background heartbeat loop
    asyncio.create_task(heartbeat_loop())


@app.get("/api/nodes")
async def get_node_statuses(session: dict = Depends(require_session)):
    """Return status, health, and stats for all 3 storage nodes."""
    statuses = await node_tracker.poll_all_nodes()
    return list(statuses.values())

@app.post("/api/nodes/{node_id}/toggle")
async def toggle_node(node_id: str, user: dict = Depends(require_admin_or_guest_authorized)):
    """Toggle real process online/offline state for a storage node via SSH (ADMIN OR AUTHORIZED GUEST)."""
    if node_id not in node_tracker.nodes_config:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' tidak ditemukan.")
    
    is_enabled = await node_tracker.toggle_node_process(node_id)
    await node_tracker.poll_all_nodes()
    return {
        "status": "success",
        "node_id": node_id,
        "is_enabled": is_enabled,
        "current_status": "online" if is_enabled else "offline"
    }


@app.get("/api/files")
def list_files(session: dict = Depends(require_session)):
    """Return catalog of stored files and their replica locations."""
    return metadata_mgr.list_all_files()

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), session: dict = Depends(require_session)):
    """
    Upload file and replicate across active storage nodes.
    Replication Factor = 2 by default.
    Accessible to both Admin and Guest.
    """
    content = await file.read()
    filename = file.filename
    size = len(content)
    content_type = file.content_type

    target_node_ids = node_tracker.select_replica_nodes(count=DEFAULT_REPLICATION_FACTOR)
    if not target_node_ids:
        raise HTTPException(
            status_code=503,
            detail="Klaster tidak tersedia: tidak ada node penyimpanan yang aktif."
        )

    temp_meta = metadata_mgr.add_file(
        filename=filename,
        size=size,
        content_type=content_type,
        node_ids=[]
    )
    file_id = temp_meta["file_id"]

    successful_nodes = []
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        for node_id in target_node_ids:
            node_url = node_tracker.nodes_config[node_id]["url"]
            try:
                res = await client.post(
                    f"{node_url}/store/{file_id}",
                    files={"file": (filename, content, content_type)}
                )
                if res.status_code == 200:
                    successful_nodes.append(node_id)
                    if node_id in node_tracker.node_status:
                        node_tracker.node_status[node_id]["file_count"] = node_tracker.node_status[node_id].get("file_count", 0) + 1
                        node_tracker.node_status[node_id]["total_size_bytes"] = node_tracker.node_status[node_id].get("total_size_bytes", 0) + size
            except Exception as e:
                print(f"[Coordinator Upload] Failed to write to {node_id}: {e}")

    if not successful_nodes:
        metadata_mgr.remove_file(file_id)
        raise HTTPException(
            status_code=500,
            detail="Gagal menyimpan replika berkas ke node yang dipilih."
        )

    metadata_mgr.files[file_id]["nodes"] = successful_nodes
    metadata_mgr.save()

    return {
        "status": "success",
        "file": metadata_mgr.get_file(file_id),
        "requested_replication": DEFAULT_REPLICATION_FACTOR,
        "actual_replicas": len(successful_nodes)
    }

@app.get("/api/download/{file_id}")
async def download_file(file_id: str, session: dict = Depends(require_session)):
    """
    Download file with failover support.
    Accessible to both Admin and Guest.
    """
    meta = metadata_mgr.get_file(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Metadata berkas tidak ditemukan.")

    nodes = meta.get("nodes", [])
    if not nodes:
        raise HTTPException(status_code=500, detail="Berkas ini tidak memiliki replika.")

    online_nodes = node_tracker.get_online_nodes()
    candidate_nodes = [nid for nid in nodes if nid in online_nodes]

    if not candidate_nodes:
        raise HTTPException(
            status_code=503,
            detail=f"Berkas '{meta['filename']}' tidak tersedia. Semua node replika ({', '.join(nodes)}) sedang mati."
        )

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        for node_id in candidate_nodes:
            node_url = node_tracker.nodes_config[node_id]["url"]
            try:
                res = await client.get(f"{node_url}/retrieve/{file_id}")
                if res.status_code == 200:
                    headers = {
                        "Content-Disposition": f'attachment; filename="{meta["filename"]}"',
                        # Lets the dashboard show which replica actually served the file (failover visibility)
                        "X-Served-By": node_id,
                        "Access-Control-Expose-Headers": "X-Served-By"
                    }
                    return Response(
                        content=res.content,
                        media_type=meta.get("content_type", "application/octet-stream"),
                        headers=headers
                    )
            except Exception as e:
                print(f"[Coordinator Download Failover] Node {node_id} failed: {e}")

    raise HTTPException(
        status_code=503,
        detail=f"Berkas '{meta['filename']}' gagal diambil dari semua replika ({', '.join(candidate_nodes)})."
    )

@app.delete("/api/files/all")
async def clear_all_files(user: dict = Depends(require_admin_or_guest_authorized)):
    """Delete all files across all storage nodes and reset metadata catalog (ADMIN OR AUTHORIZED GUEST)."""
    all_files = metadata_mgr.list_all_files()
    deleted_count = 0

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        for meta in all_files:
            file_id = meta.get("file_id")
            nodes = meta.get("nodes", [])
            for node_id in nodes:
                if node_id in node_tracker.nodes_config:
                    node_url = node_tracker.nodes_config[node_id]["url"]
                    try:
                        await client.delete(f"{node_url}/delete/{file_id}")
                    except Exception as e:
                        print(f"[Coordinator Clear All] Error deleting {file_id} from {node_id}: {e}")
            metadata_mgr.remove_file(file_id)
            deleted_count += 1

    metadata_mgr.files = {}
    metadata_mgr.save()

    return {
        "status": "success",
        "message": f"Successfully deleted all {deleted_count} files from cluster",
        "deleted_count": deleted_count
    }

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str, user: dict = Depends(require_admin_or_guest_authorized)):
    """Delete file from all storage nodes and metadata catalog (ADMIN OR AUTHORIZED GUEST)."""
    meta = metadata_mgr.get_file(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Metadata berkas tidak ditemukan.")

    nodes = meta.get("nodes", [])
    deleted_from = []

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        for node_id in nodes:
            if node_id in node_tracker.nodes_config:
                node_url = node_tracker.nodes_config[node_id]["url"]
                try:
                    res = await client.delete(f"{node_url}/delete/{file_id}")
                    if res.status_code == 200:
                        deleted_from.append(node_id)
                except Exception as e:
                    print(f"[Coordinator Delete] Error deleting from {node_id}: {e}")

    metadata_mgr.remove_file(file_id)
    return {
        "status": "deleted",
        "file_id": file_id,
        "filename": meta["filename"],
        "removed_from": deleted_from
    }

# Serve Web Dashboard Static UI
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>Web UI index.html loading...</h2>")
