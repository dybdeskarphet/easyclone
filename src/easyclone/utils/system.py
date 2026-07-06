import os
from shutil import which
from easyclone.utils.logging import log

def is_tool(name: str) -> bool:
    return which(name) is not None

def exit_if_no_rclone() -> None:
    from easyclone.core.types import LogLevel
    if not is_tool("rclone"):
        log(
            "Rclone is not installed on your system, 'rclone' command should be in the $PATH.",
            LogLevel.ERROR,
        )
        exit(1)

def exit_if_currently_running() -> None:
    from easyclone.core.types import LogLevel
    if os.path.exists("/tmp/easyclone.sock"):
        log(
            "Easyclone is already running. Delete /tmp/easyclone.sock if you think this is a mistake.",
            LogLevel.WARN,
        )
        exit(1)
