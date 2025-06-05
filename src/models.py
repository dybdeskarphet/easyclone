from pydantic import BaseModel

class BackupConfig(BaseModel):
    sync_paths: list[str]
    backup_paths: list[str]
    remote_name: str
    root_dir: str

class RcloneConfig(BaseModel):
    args: list[str]

class Config(BaseModel):
    backup: BackupConfig
    rclone: RcloneConfig
