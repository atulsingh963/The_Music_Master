import os
from pathlib import Path


def get_project_root() -> Path:
    """Returns root directory of the project."""
    return Path(__file__).resolve().parent.parent.parent.parent


def get_soundfonts_dir() -> Path:
    """Returns soundfonts storage directory."""
    path = get_project_root() / "soundfonts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_recordings_dir() -> Path:
    """Returns recordings output directory."""
    path = get_project_root() / "recordings"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_user_data_dir() -> Path:
    """Returns local user configuration and database directory."""
    appdata = os.getenv("APPDATA")
    if appdata:
        base = Path(appdata) / "MusicMaster"
    else:
        base = Path.home() / ".music_master"
    base.mkdir(parents=True, exist_ok=True)
    return base
