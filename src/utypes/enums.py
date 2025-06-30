from enum import Enum

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
