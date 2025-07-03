import asyncio
from easyclone.config import cfg
from easyclone.rclone.backup import backup
from easyclone.rclone.create_dirs import create_dir_tree, create_dirs_array, traverse_and_create_folders_by_depth
from easyclone.utils.path_manipulation import organize_paths
from easyclone.utypes.enums import CommandType

async def backup_copy_operation(verbose: bool):
    copy_paths = organize_paths(cfg.backup.copy_paths, cfg.backup.remote_name)
    copy_task_semaphore = asyncio.Semaphore(cfg.rclone.concurrent_limit)
    copy_dirs_task_semaphore = asyncio.Semaphore(cfg.rclone.concurrent_limit)
    copy_dirs_array = create_dirs_array(copy_paths)
    copy_dirs_root = create_dir_tree(copy_dirs_array)

    _copy_folders_create_operation = await traverse_and_create_folders_by_depth(
        root=copy_dirs_root,
        verbose=verbose,
        semaphore=copy_dirs_task_semaphore
    )
    _copy_operation = await backup(
        paths=copy_paths,
        command_type=CommandType.COPY,
        rclone_args=cfg.rclone.args,
        semaphore=copy_task_semaphore,
        verbose=verbose
    )


async def backup_sync_operation(verbose: bool):
    sync_paths = organize_paths(cfg.backup.sync_paths, cfg.backup.remote_name)
    sync_task_semaphore = asyncio.Semaphore(cfg.rclone.concurrent_limit)
    sync_dirs_task_semaphore = asyncio.Semaphore(cfg.rclone.concurrent_limit)
    sync_dirs_array = create_dirs_array(sync_paths)
    sync_dirs_root = create_dir_tree(sync_dirs_array)

    _sync_folders_create_operation = await traverse_and_create_folders_by_depth(
        root=sync_dirs_root,
        verbose=verbose,
        semaphore=sync_dirs_task_semaphore
    )

    _sync_operation = await backup(
        paths=sync_paths,
        command_type=CommandType.COPY,
        rclone_args=cfg.rclone.args,
        semaphore=sync_task_semaphore,
        verbose=verbose
    )
