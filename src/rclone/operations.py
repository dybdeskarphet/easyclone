import asyncio
from config import load_config
from rclone.backup import backup
from rclone.dirs import create_dir_tree, create_dirs_array, traverse_and_create_folders_by_depth
from utils import organize_paths
from utypes.enums import CommandType

async def backup_copy_operation(verbose: bool):
    config = load_config()
    root_dir = str((config.backup.root_dir)).rstrip("/")

    copy_paths = organize_paths(config.backup.copy_paths, config.backup.remote_name, root_dir)

    copy_task_semaphore = asyncio.Semaphore(config.rclone.concurrent_limit)

    copy_dirs_task_semaphore = asyncio.Semaphore(config.rclone.concurrent_limit)

    copy_dirs_array = create_dirs_array(copy_paths)
    copy_dirs_root = create_dir_tree(copy_dirs_array)

    _copy_folders_create_operation = await traverse_and_create_folders_by_depth(copy_dirs_root, verbose, copy_dirs_task_semaphore)
    _copy_operation = await backup(paths=copy_paths, command_type=CommandType.COPY, rclone_args=config.rclone.args, semaphore=copy_task_semaphore, verbose=verbose)


async def backup_sync_operation(verbose: bool):
    config = load_config()
    root_dir = str((config.backup.root_dir)).rstrip("/")

    sync_paths = organize_paths(config.backup.sync_paths, config.backup.remote_name, root_dir)

    sync_task_semaphore = asyncio.Semaphore(config.rclone.concurrent_limit)

    sync_dirs_task_semaphore = asyncio.Semaphore(config.rclone.concurrent_limit)

    sync_dirs_array = create_dirs_array(sync_paths)
    sync_dirs_root = create_dir_tree(sync_dirs_array)

    _sync_folders_create_operation = await traverse_and_create_folders_by_depth(sync_dirs_root, verbose, sync_dirs_task_semaphore)

    _sync_operation = await backup(paths=sync_paths, command_type=CommandType.COPY, rclone_args=config.rclone.args, semaphore=sync_task_semaphore, verbose=verbose)
