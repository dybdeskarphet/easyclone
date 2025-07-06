from __future__ import annotations
import asyncio
from easyclone.shared import sync_status
from easyclone.utils.essentials import log
from easyclone.utypes.models import PathItem
from easyclone.utypes.enums import BackupLog, BackupStatus, LogLevel, PathType, RcloneOperationType
import os
from pathlib import Path
from collections import deque
from easyclone.config import cfg

class DirNode:
    def __init__(self, name: str, details: PathItem):
        self.name: str = name
        self.details: PathItem = details
        self.children: list[DirNode] = []

    def find_child(self, name: str) -> "DirNode | None":
        for child in self.children:
            if child.name == name:
                return child
        return None

    def add_child(self, name: str, details: PathItem) -> "DirNode":
        existing = self.find_child(name)
        if existing:
            return existing
        new_child = DirNode(name, details)
        self.children.append(new_child)
        return new_child

    def print_tree(self, level: int=0):
        indent = "  " * level
        print(f"{indent}- {self.name} ({self.details.get('dest')})")
        for child in sorted(self.children, key=lambda c: c.name):
            child.print_tree(level + 1)

def create_dirs_array(path_list: list[PathItem]):
    only_dirs: list[PathItem] = []

    for path in path_list:
        new_dir_path: PathItem

        if path.get("type") == "dir":
            new_dir_path = path
        else:
            new_dir_path = {
                "source": os.path.dirname(path.get("source")),
                "dest": path.get("dest"),
                "path_type": PathType.DIR.value
            }

        if new_dir_path not in only_dirs:
            only_dirs.append(new_dir_path)

    return only_dirs

def create_dir_tree(path_list: list[PathItem]):
    root = DirNode("Root", {"source": "/", "dest": f"{cfg.backup.remote_name}:{cfg.backup.root_dir}", "path_type": "dir",})

    for path_item in path_list:
        source_str = path_item.get("source")
        dest_str = path_item.get("dest")
    
        source_parts = Path(source_str).parts
        dest_main, _, dest_path = dest_str.partition(":")

        if dest_path:
            dest_parts = Path(dest_path).parts
        else:
            dest_parts = []
    
        current = root
    
        for i in range(1, len(source_parts)):
            source_sub_path = str(Path(*source_parts[:i+1]))

            if dest_path:
                dest_sub_path = f"{dest_main}:{Path(*dest_parts[:i+2])}"
            else:
                dest_sub_path = ""
    
            node_details: PathItem = {
                "source": source_sub_path,
                "dest": dest_sub_path,
                "path_type": PathType.DIR.value
            }
    
            part_name = source_parts[i]
            current = current.add_child(part_name, node_details)

    return root

async def create_folder_command(source: str, dest: str, verbose: bool):
    lsd_cmd = ["rclone", "lsd", dest]
    log(f"Checking if directory exist at {dest}", BackupLog.WAIT)

    process = await asyncio.create_subprocess_exec(*lsd_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        log(f"Directory exist at {dest}", BackupLog.OK)
        return

    mkdir_cmd = ["rclone", "mkdir", dest]

    log(f"Creating a directory at {dest}", BackupLog.WAIT)
    process = await asyncio.create_subprocess_exec(*mkdir_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    process_id = await sync_status.add_operation(source=source, dest=dest, path_type=PathType.DIR.value, status=BackupStatus.IN_PROGRESS, operation_type=RcloneOperationType.MKDIR)

    stdout, stderr = await process.communicate()
    stdout = stdout.decode(errors="ignore").strip()
    stderr = stderr.decode(errors="ignore").strip()

    match process.returncode:
        case 0:
            log(f"Directory created successfully: {dest}", BackupLog.OK)
        case 1:
            log(f"Couldn't create the directory: {dest}", BackupLog.ERR)
        case _:
            log(f"Operation failed with {process.returncode} exit code: {dest}", BackupLog.ERR)

    await sync_status.delete_operation(process_id)

    if verbose:
        if stderr: 
            log(f"{stderr}", LogLevel.WARN)
        if stdout:
            log(f"{stdout}", LogLevel.LOG)

async def create_folders_on_remote(nodes: list[DirNode], semaphore: asyncio.Semaphore, verbose: bool):
    async def mkdir_task(source: str, dest: str):
        async with semaphore:
            await create_folder_command(source, dest, verbose)

    tasks = [mkdir_task(node.details.get("source"), node.details.get("dest")) for node in nodes]

    _ = await asyncio.gather(*tasks)

async def traverse_and_create_folders_by_depth(root: DirNode, verbose: bool, semaphore: asyncio.Semaphore):
    queue = deque([(root, 0)])
    current_depth = 0
    current_level_nodes: list[DirNode] = []

    while queue:
        node, depth = queue.popleft()

        if depth != current_depth:
            await create_folders_on_remote(current_level_nodes, semaphore, verbose)
            current_level_nodes = []
            current_depth = depth

        current_level_nodes.append(node)

        for child in node.children:
            queue.append((child, depth + 1))

    if current_level_nodes:
        await create_folders_on_remote(current_level_nodes, semaphore, verbose)
