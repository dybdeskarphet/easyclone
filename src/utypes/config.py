from pydantic import BaseModel

# TODO: Make this config thingy more global using singletons

class BackupConfig(BaseModel):
    sync_paths: list[str]
    copy_paths: list[str]
    remote_name: str
    root_dir: str
    verbose_log: bool

class RcloneConfig(BaseModel):
    args: list[str]
    concurrent_limit: int

class Config(BaseModel):
    backup: BackupConfig
    rclone: RcloneConfig
