from easyclone.utypes.enums import LogLevel, BackupLog

def log(message: str, logtype: LogLevel | BackupLog) -> None:
    color = "\033[32;1m"

    match logtype:
        case LogLevel.ERROR | BackupLog.ERR:
            # RED
            color = "\033[31;1m"
        case LogLevel.LOG:
            # BLUE
            color = "\033[34;1m"
        case LogLevel.INFO | BackupLog.OK:
            # GREEN
            color = "\033[32;1m"
        case LogLevel.WARN | BackupLog.WAIT:
            # YELLOW
            color = "\033[33;1m"

    full_msg = f"{color}{logtype.value}"
    if(isinstance(logtype, LogLevel)):
        full_msg = full_msg + ":"

    print(f"{full_msg}\033[0m {message}")
