"""Multi-track project data model and persistence (JSON/compressed) for Music Master."""

import gzip
import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from music_master.midi.file import NoteEvent


@dataclass
class StudioTrack:
    """Represents a single musical track in a project."""

    id: str
    name: str
    instrument_id: str
    channel: int = 0
    volume: float = 1.0
    pan: float = 0.0
    muted: bool = False
    solo: bool = False
    notes: List[NoteEvent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "instrument_id": self.instrument_id,
            "channel": self.channel,
            "volume": self.volume,
            "pan": self.pan,
            "muted": self.muted,
            "solo": self.solo,
            "notes": [asdict(n) for n in self.notes],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudioTrack":
        notes_data = data.get("notes", [])
        notes = [NoteEvent(**n) for n in notes_data]
        return cls(
            id=data.get("id", "track-1"),
            name=data.get("name", "Track 1"),
            instrument_id=data.get("instrument_id", "harmonium"),
            channel=data.get("channel", 0),
            volume=float(data.get("volume", 1.0)),
            pan=float(data.get("pan", 0.0)),
            muted=bool(data.get("muted", False)),
            solo=bool(data.get("solo", False)),
            notes=notes,
        )


@dataclass
class StudioProject:
    """Complete Music Master project specification and state."""

    name: str = "Untitled Project"
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    bpm: float = 120.0
    time_signature_num: int = 4
    time_signature_den: int = 4
    key_root: str = "C"
    scale_type: str = "Major"
    tracks: List[StudioTrack] = field(default_factory=list)
    master_volume: float = 0.85
    settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "bpm": self.bpm,
            "time_signature_num": self.time_signature_num,
            "time_signature_den": self.time_signature_den,
            "key_root": self.key_root,
            "scale_type": self.scale_type,
            "master_volume": self.master_volume,
            "settings": self.settings,
            "tracks": [t.to_dict() for t in self.tracks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudioProject":
        tracks_data = data.get("tracks", [])
        tracks = [StudioTrack.from_dict(t) for t in tracks_data]
        return cls(
            name=data.get("name", "Untitled Project"),
            version=data.get("version", "1.0.0"),
            created_at=float(data.get("created_at", time.time())),
            modified_at=float(data.get("modified_at", time.time())),
            bpm=float(data.get("bpm", 120.0)),
            time_signature_num=int(data.get("time_signature_num", 4)),
            time_signature_den=int(data.get("time_signature_den", 4)),
            key_root=data.get("key_root", "C"),
            scale_type=data.get("scale_type", "Major"),
            master_volume=float(data.get("master_volume", 0.85)),
            settings=data.get("settings", {}),
            tracks=tracks,
        )


class ProjectManager:
    """Handles saving, loading, and autosaving Music Master projects."""

    def __init__(self, current_project: Optional[StudioProject] = None) -> None:
        self.project = current_project or self.create_new_project()
        self.current_filepath: Optional[str] = None
        self.is_dirty: bool = False

    def create_new_project(self, name: str = "New Song") -> StudioProject:
        proj = StudioProject(name=name)
        # Default default tracks
        proj.tracks = [
            StudioTrack(id="t1", name="Harmonium Melody", instrument_id="harmonium", channel=0),
            StudioTrack(id="t2", name="Piano Chords", instrument_id="grand_piano", channel=1),
        ]
        self.project = proj
        self.current_filepath = None
        self.is_dirty = False
        return proj

    def save_project(self, filepath: str, compressed: bool = False) -> None:
        """Saves the project to JSON or gzip-compressed JSON (.mmp / .mmpz)."""
        self.project.modified_at = time.time()
        data = self.project.to_dict()

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        if compressed or filepath.endswith(".mmpz"):
            with gzip.open(filepath, "wt", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        self.current_filepath = filepath
        self.is_dirty = False

    def load_project(self, filepath: str) -> StudioProject:
        """Loads a project from a .mmp or .mmpz file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Project file not found: {filepath}")

        try:
            with gzip.open(filepath, "rt", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

        self.project = StudioProject.from_dict(data)
        self.current_filepath = filepath
        self.is_dirty = False
        return self.project
