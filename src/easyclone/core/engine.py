import asyncio
from easyclone.config import cfg
from easyclone.rclone.client import backup
from easyclone.rclone.tree import (
    create_dir_tree,
    create_dirs_array,
    traverse_and_create_folders_by_depth,
)
from easyclone.core.state import sync_status
from easyclone.utils.logging import log
from easyclone.utils.path import organize_paths
from easyclone.core.types import CommandType, LogLevel


def make_backup_operation(
    command_type: CommandType, paths_config: list[str], verbose: bool
):
    async def backup_operation():
        paths = organize_paths(paths_config, cfg.backup.remote_name)
        task_semaphore = asyncio.Semaphore(cfg.rclone.concurrent_limit)
        dirs_task_semaphore = asyncio.Semaphore(cfg.rclone.concurrent_limit)
        dirs_array = create_dirs_array(paths["valid_paths"])
        dirs_root = create_dir_tree(dirs_array)

        if paths["empty_paths"]:
            log(
                f"Below paths couldn't be found:\n{'\n'.join(paths['empty_paths'])}\n",
                LogLevel.WARN,
            )
            for path in paths["empty_paths"]:
                await sync_status.add_empty_path(path)

        _copy_folders_create_operation = await traverse_and_create_folders_by_depth(
            root=dirs_root, rclone_args=cfg.rclone.args, verbose=verbose, semaphore=dirs_task_semaphore
        )
        _copy_operation = await backup(
            paths=paths["valid_paths"],
            command_type=command_type,
            rclone_args=cfg.rclone.args,
            semaphore=task_semaphore,
            verbose=verbose,
        )

    return backup_operation
