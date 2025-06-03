from pathlib import Path
from enums import LogLevel

def log(message: str, level: LogLevel = LogLevel.LOG) -> None:
    match level:
        case LogLevel.ERROR:
            print(f"\033[31;1merror:\033[0m {message}")
        case LogLevel.LOG:
            print(f"\033[34;1mlog:\033[0m {message}")
        case LogLevel.INFO:
            print(f"\033[32;1minfo:\033[0m {message}")
        case LogLevel.WARN:
            print(f"\033[33;1mwarn:\033[0m {message}")

# TODO: Doesn't backup to the right directory when it's a directory
def organize_paths(paths: list[str], remote_name: str, root_dir: str) -> list[dict[str,str]]:
    source_dest_array: list[dict[str, str]] = []

    for path in paths:
        p = Path(path).expanduser()

        if p.is_dir():
            dest_dir = p.parent
            source_dest_array.append({f"{p}": f"{remote_name}:{root_dir}{dest_dir}"})
        elif p.is_file():
            source_dest_array.append({f"{p}": f"{remote_name}:{root_dir}{p}"})

    return source_dest_array
