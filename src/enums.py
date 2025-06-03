from enum import Enum

class LogLevel(Enum):
    ERROR = "error"
    LOG = "log"
    INFO = "info"
    WARN = "warn"

class CommandType(Enum):
    COPY = "copy"
    SYNC = "sync"

class PathType(Enum):
    FILE = "file"
    DIR = "dir"
