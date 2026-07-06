from enum import Enum
from typing import TypedDict

class LogLevel(Enum):
    ERROR = "error"
    LOG = "log"
    INFO = "info"
    WARN = "warn"


class BackupLog(Enum):
    OK = "✓"
    ERR = "⛌"
    WAIT = ""


class CommandType(Enum):
    COPY = "copy"
    SYNC = "sync"


class PathType(Enum):
    FILE = "file"
    DIR = "dir"


class BackupStatus(Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class RcloneOperationType(Enum):
    BACKUP = "backup"
    MKDIR = "mkdir"


class FindMissingOptions(Enum):
    copy = "copy"
    sync = "sync"
    all = "all"


class PathItem(TypedDict):
    source: str
    dest: str
    path_type: str


class SyncStatusItem(PathItem):
    id: str
    status: str
    operation_type: str


class OrganizedPaths(TypedDict):
    valid_paths: list[PathItem]
    empty_paths: list[str]
