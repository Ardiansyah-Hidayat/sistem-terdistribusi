"""
auth_manager.py - Manages authentication, sessions, and role-based permissions
Roles:
- 'admin': Full access (username: ardi, pass: ardi123)
- 'guest': Can upload and download. If guest_authority_enabled is True, guest can also delete and simulate failure!
"""
import json
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException

AUTH_STATE_FILE = Path(__file__).resolve().parent.parent / "auth_state.json"
ADMIN_USERNAME = "ardi"
ADMIN_PASSWORD = "ardi123"

class AuthManager:
    def __init__(self):
        self.state_file = AUTH_STATE_FILE
        self.guest_access_enabled = True
        self.guest_authority_enabled = False  # If True, guests can delete & simulate failure
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.load_state()

    def load_state(self):
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                self.guest_access_enabled = data.get("guest_access_enabled", True)
                self.guest_authority_enabled = data.get("guest_authority_enabled", False)
            except Exception as e:
                print(f"[AuthManager] Error loading state: {e}")
                self.guest_access_enabled = True
                self.guest_authority_enabled = False
        else:
            self.save_state()

    def save_state(self):
        try:
            self.state_file.write_text(
                json.dumps({
                    "guest_access_enabled": self.guest_access_enabled,
                    "guest_authority_enabled": self.guest_authority_enabled
                }, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"[AuthManager] Error saving state: {e}")

    def login_admin(self, username: str, password: str) -> Dict[str, Any]:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            token = f"admin_{uuid.uuid4().hex}"
            self.sessions[token] = {
                "role": "admin",
                "username": ADMIN_USERNAME,
                "created_at": time.time()
            }
            return {
                "status": "success",
                "token": token,
                "role": "admin",
                "username": ADMIN_USERNAME,
                "guest_access_enabled": self.guest_access_enabled,
                "guest_authority_enabled": self.guest_authority_enabled
            }
        raise HTTPException(status_code=401, detail="Username atau password admin salah!")

    def login_guest(self) -> Dict[str, Any]:
        if not self.guest_access_enabled:
            raise HTTPException(
                status_code=403,
                detail="Akses Guest sedang dinonaktifkan oleh Admin."
            )
        token = f"guest_{uuid.uuid4().hex}"
        self.sessions[token] = {
            "role": "guest",
            "username": "Guest",
            "created_at": time.time()
        }
        return {
            "status": "success",
            "token": token,
            "role": "guest",
            "username": "Guest",
            "guest_access_enabled": self.guest_access_enabled,
            "guest_authority_enabled": self.guest_authority_enabled
        }

    def logout(self, token: str):
        if token in self.sessions:
            del self.sessions[token]

    def set_guest_access(self, enabled: bool):
        self.guest_access_enabled = enabled
        self.save_state()
        if not enabled:
            # Revoke all active guest sessions
            tokens_to_remove = [t for t, s in self.sessions.items() if s.get("role") == "guest"]
            for t in tokens_to_remove:
                del self.sessions[t]
        return self.guest_access_enabled

    def set_guest_authority(self, enabled: bool):
        self.guest_authority_enabled = enabled
        self.save_state()
        return self.guest_authority_enabled

    def get_session(self, token: Optional[str]) -> Dict[str, Any]:
        if not token or token not in self.sessions:
            raise HTTPException(status_code=401, detail="Sesi login tidak valid atau sudah kedaluwarsa.")
        
        session = self.sessions[token]
        # If user is guest and guest access was turned off, reject
        if session.get("role") == "guest" and not self.guest_access_enabled:
            del self.sessions[token]
            raise HTTPException(status_code=403, detail="Akses Guest telah dinonaktifkan oleh Administrator.")
            
        return session

    def require_admin(self, token: Optional[str]) -> Dict[str, Any]:
        session = self.get_session(token)
        if session.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Akses ditolak: Operasi ini membutuhkan hak akses Administrator!"
            )
        return session

    def require_admin_or_guest_authorized(self, token: Optional[str]) -> Dict[str, Any]:
        session = self.get_session(token)
        if session.get("role") == "admin":
            return session
        if session.get("role") == "guest" and self.guest_authority_enabled:
            return session
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak: Izin eksperimen guest (delete/simulate failure) sedang dinonaktifkan oleh Admin!"
        )
