from pathlib import Path
import os
from easyclone.utypes.enums import PathType
from easyclone.utypes.models import OrganizedPaths, PathItem

def organize_paths(paths: list[str], remote_name: str) -> OrganizedPaths:
    from easyclone.config import cfg
    source_dest_array: list[PathItem] = []
    empty_paths: list[str] = []
    root_dir = cfg.backup.root_dir

    for path in paths:
        p = Path(path).expanduser()

        if not os.path.exists(p):
            empty_paths.append(path)

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

    return { 
        "valid_paths": source_dest_array,
        "empty_paths": empty_paths
    }

def collapseuser(path: str) -> str:
    """
    Opposite of path.expanduser()
    """
    home = os.path.expanduser("~")
    if path.startswith(home):
        return path.replace(home, "~", 1)
    return path
