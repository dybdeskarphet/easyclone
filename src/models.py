from typing import TypedDict
from pydantic import BaseModel

class BackupConfig(BaseModel):
    sync_paths: list[str]
    backup_paths: list[str]
    remote_name: str
    root_dir: str

class RcloneConfig(BaseModel):
    args: list[str]
    concurrent_limit: int

class Config(BaseModel):
    backup: BackupConfig
    rclone: RcloneConfig

class SyncStatusItem(TypedDict):
    id: str
    source: str
    dest: str
    status: str
