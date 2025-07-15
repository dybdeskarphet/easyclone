from pydantic import BaseModel

class BackupConfigModel(BaseModel):
    sync_paths: list[str]
    copy_paths: list[str]
    remote_name: str
    root_dir: str
    verbose_log: bool = False

class RcloneConfigModel(BaseModel):
    args: list[str] = [
        "--update",
        "--verbose",
        "--transfers 30",
        "--checkers 8",
        "--contimeout 60s",
        "--timeout 300s",
        "--retries 3",
        "--low-level-retries 10",
        "--stats 1s"
    ]
    concurrent_limit: int = 50

class ConfigModel(BaseModel):
    backup: BackupConfigModel
    rclone: RcloneConfigModel = RcloneConfigModel()
