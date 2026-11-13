from pathlib import Path

from pydantic import BaseModel, Field

from music_master.utils.paths import get_user_data_dir


class AudioConfig(BaseModel):
    sample_rate: int = 44100
    buffer_size: int = 512
    channels: int = 2
    device_id: int | None = None
    polyphony: int = 64
    master_volume: float = 0.85


class UIConfig(BaseModel):
    theme: str = "dark"
    window_width: int = 1200
    window_height: int = 800
    start_maximized: bool = False


class Config(BaseModel):
    app_name: str = "Music Master"
    version: str = "0.1.0"
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file_path: Path = Field(default_factory=lambda: get_user_data_dir() / "music_master.log")
    database_path: Path = Field(default_factory=lambda: get_user_data_dir() / "music_master.db")
    audio: AudioConfig = Field(default_factory=AudioConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
