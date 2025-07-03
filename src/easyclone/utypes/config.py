from pydantic import BaseModel

class BackupConfigModel(BaseModel):
    sync_paths: list[str]
    copy_paths: list[str]
    remote_name: str
    root_dir: str
    verbose_log: bool

class RcloneConfigModel(BaseModel):
    args: list[str]
    concurrent_limit: int

class ConfigModel(BaseModel):
    backup: BackupConfigModel
    rclone: RcloneConfigModel
