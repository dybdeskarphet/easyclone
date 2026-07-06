import re
from pydantic import BaseModel, field_validator, model_validator

RCLONE_DURATION_RE = re.compile(r"^(\d+(ms|s|m|h|d|w|M|y))+$")


class VersioningModel(BaseModel):
    enable: bool = False
    remote_name: str | None = None
    path: str | None = None
    timestamp: str = "%Y-%m-%d_%H-%M-%S"
    prune_timeout: str | None = None

    @model_validator(mode="after")
    def validate_and_normalize_path(self):
        if not self.enable:
            return self

        if not self.path or not self.path.strip():
            raise ValueError("path must be specified when versioning is enabled")

        self.path = self.path.strip("/")
        return self

    @field_validator("prune_timeout")
    @classmethod
    def validate_rclone_duration(cls, v: str | None):
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not RCLONE_DURATION_RE.match(v):
                raise ValueError(
                    "prune_timeout must be a valid Rclone duration (e.g., '30d', '24h', '1h30m')"
                )

        return v


class BackupConfigModel(BaseModel):
    sync_paths: list[str]
    copy_paths: list[str]
    remote_name: str
    root_dir: str
    verbose_log: bool = False
    versioning: VersioningModel = VersioningModel()


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
        "--stats 1s",
    ]
    concurrent_limit: int = 50


class DaemonConfigModel(BaseModel):
    interval: int = 60
    countdown: bool = False


class ConfigModel(BaseModel):
    backup: BackupConfigModel
    rclone: RcloneConfigModel = RcloneConfigModel()
    daemon: DaemonConfigModel = DaemonConfigModel()
