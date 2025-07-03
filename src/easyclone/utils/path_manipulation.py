from pathlib import Path
import os
from easyclone.utypes.enums import PathType
from easyclone.utypes.models import PathItem

def organize_paths(paths: list[str], remote_name: str) -> list[PathItem]:
    from easyclone.config import cfg
    source_dest_array: list[PathItem] = []
    root_dir = cfg.backup.root_dir

    for path in paths:
        p = Path(path).expanduser()

        if p.is_dir():
            source_dest_array.append({
                "source": f"{p}",
                "dest": f"{remote_name}:{root_dir}{p}",
                "path_type": PathType.DIR.value
            })
        elif p.is_file():
            dest_dir = p.parent
            source_dest_array.append({
                "source": f"{p}",
                "dest": f"{remote_name}:{root_dir}{dest_dir}",
                "path_type": PathType.FILE.value
            })

    return source_dest_array

def collapseuser(path: str) -> str:
    """
    Opposite of path.expanduser()
    """
    home = os.path.expanduser("~")
    if path.startswith(home):
        return path.replace(home, "~", 1)
    return path
