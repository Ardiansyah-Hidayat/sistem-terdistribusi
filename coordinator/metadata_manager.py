import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class MetadataManager:
    def __init__(self, metadata_path: Path):
        self.metadata_path = Path(metadata_path)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        self.files: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        """Load file catalog metadata from JSON disk file."""
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.files = json.load(f)
            except Exception as e:
                print(f"[Coordinator Metadata] Failed to parse {self.metadata_path}: {e}")
                self.files = {}
        else:
            self.files = {}

    def save(self):
        """Persist metadata catalog to JSON file."""
        try:
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.files, f, indent=2)
        except Exception as e:
            print(f"[Coordinator Metadata] Failed to save {self.metadata_path}: {e}")

    def add_file(self, filename: str, size: int, content_type: str, node_ids: List[str], file_id: Optional[str] = None) -> Dict[str, Any]:
        """Register a new file entry and its node replica assignments."""
        if not file_id:
            file_id = str(uuid.uuid4())[:8] + "_" + filename.replace(" ", "_")

        entry = {
            "file_id": file_id,
            "filename": filename,
            "size": size,
            "content_type": content_type or "application/octet-stream",
            "created_at": datetime.now().isoformat(),
            "nodes": node_ids
        }
        self.files[file_id] = entry
        self.save()
        return entry

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a specific file."""
        return self.files.get(file_id)

    def remove_file(self, file_id: str) -> bool:
        """Delete file metadata entry."""
        if file_id in self.files:
            del self.files[file_id]
            self.save()
            return True
        return False

    def list_all_files(self) -> List[Dict[str, Any]]:
        """Return list of all registered files."""
        return list(self.files.values())
