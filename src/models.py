from typing import TypedDict
from pydantic import BaseModel

class BackupConfig(BaseModel):
    sync_paths: list[str]
    copy_paths: list[str]
    remote_name: str
    root_dir: str

class RcloneConfig(BaseModel):
    args: list[str]
    concurrent_limit: int

class Config(BaseModel):
    backup: BackupConfig
    rclone: RcloneConfig

class PathItem(TypedDict):
    source: str
    dest: str
    type: str

class SyncStatusItem(PathItem):
    id: str
    status: str
