import json
from ntpath import expanduser
from pathlib import Path
import os
from easyclone.core.types import FindMissingOptions, PathType, OrganizedPaths, PathItem


def organize_paths(paths: list[str], remote_name: str) -> OrganizedPaths:
    from easyclone.config import cfg

    source_dest_array: list[PathItem] = []
    empty_paths: list[str] = []
    root_dir = cfg.backup.root_dir

    for path in paths:
        p = Path(os.path.expandvars(os.path.expanduser(path)))

        if not os.path.exists(p):
            empty_paths.append(path)

        if p.is_dir():
            source_dest_array.append(
                {
                    "source": f"{p}",
                    "dest": f"{remote_name}:{root_dir}{p}",
                    "path_type": PathType.DIR.value,
                }
            )
        elif p.is_file():
            dest_dir = p.parent
            source_dest_array.append(
                {
                    "source": f"{p}",
                    "dest": f"{remote_name}:{root_dir}{dest_dir}",
                    "path_type": PathType.FILE.value,
                }
            )

    return {"valid_paths": source_dest_array, "empty_paths": empty_paths}


def collapseuser(path: str) -> str:
    """
    Opposite of path.expanduser()
    """
    home = os.path.expanduser("~")
    if path.startswith(home):
        return path.replace(home, "~", 1)
    return path


def find_missing(
    recursive=False, list_type: FindMissingOptions = FindMissingOptions.all
):
    from easyclone.config import cfg

    filter_list: list[str] = []

    if list_type is FindMissingOptions.all:
        filter_list += cfg.backup.copy_paths + cfg.backup.sync_paths
    elif list_type is FindMissingOptions.copy:
        filter_list += cfg.backup.copy_paths
    elif list_type is FindMissingOptions.sync:
        filter_list += cfg.backup.sync_paths

    filter_paths = [
        Path(os.path.expandvars(os.path.expanduser(p))).absolute() for p in filter_list
    ]

    cwd_path = Path.cwd()
    cwd_func = cwd_path.rglob("*") if recursive else cwd_path.iterdir()

    if recursive:
        missing = [
            str(item)
            for item in cwd_func
            if not any(item.is_relative_to(fp) for fp in filter_paths)
        ]
    else:
        cwd_content = [str(item) for item in cwd_func]
        filter_content = [str(fp) for fp in filter_paths]
        missing = list(set(cwd_content) - set(filter_content))

    return missing
