import os
from pathlib import Path
from typing import Dict, Any, List

class StorageService:
    def __init__(self, node_id: str, storage_dir: Path):
        self.node_id = node_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, file_id: str) -> Path:
        # Sanitize file_id to prevent directory traversal
        clean_name = os.path.basename(file_id)
        return self.storage_dir / clean_name

    def save_file(self, file_id: str, content: bytes) -> Dict[str, Any]:
        file_path = self._get_file_path(file_id)
        with open(file_path, "wb") as f:
            f.write(content)
        
        size = len(content)
        return {
            "node_id": self.node_id,
            "file_id": file_id,
            "size": size,
            "status": "stored"
        }

    def read_file(self, file_id: str) -> bytes:
        file_path = self._get_file_path(file_id)
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_id} not found on {self.node_id}")
        
        with open(file_path, "rb") as f:
            return f.read()

    def delete_file(self, file_id: str) -> bool:
        file_path = self._get_file_path(file_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def list_files(self) -> List[str]:
        return [f.name for f in self.storage_dir.iterdir() if f.is_file()]

    def get_stats(self) -> Dict[str, Any]:
        files = self.list_files()
        total_size = sum(
            (self.storage_dir / filename).stat().st_size for filename in files
        )
        return {
            "node_id": self.node_id,
            "file_count": len(files),
            "total_size_bytes": total_size,
            "files": files
        }
