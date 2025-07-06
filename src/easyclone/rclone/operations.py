import asyncio
from easyclone.config import cfg
from easyclone.rclone.backup import backup
from easyclone.rclone.create_dirs import create_dir_tree, create_dirs_array, traverse_and_create_folders_by_depth
from easyclone.shared import sync_status
from easyclone.utils.essentials import log
from easyclone.utils.path_manipulation import organize_paths
from easyclone.utypes.enums import CommandType, LogLevel

def make_backup_operation(command_type: CommandType, paths_config: list[str], verbose: bool):
    async def backup_operation():
        paths = organize_paths(paths_config, cfg.backup.remote_name)
        task_semaphore = asyncio.Semaphore(cfg.rclone.concurrent_limit)
        dirs_task_semaphore = asyncio.Semaphore(cfg.rclone.concurrent_limit)
        dirs_array = create_dirs_array(paths["valid_paths"])
        dirs_root = create_dir_tree(dirs_array)

        log(f"Below paths couldn't be found:\n{"\n".join(paths["empty_paths"])}\n", LogLevel.WARN)
        for path in paths["empty_paths"]:
            await sync_status.add_empty_path(path)

        _copy_folders_create_operation = await traverse_and_create_folders_by_depth(
            root=dirs_root,
            verbose=verbose,
            semaphore=dirs_task_semaphore
        )
        _copy_operation = await backup(
            paths=paths["valid_paths"],
            command_type=command_type,
            rclone_args=cfg.rclone.args,
            semaphore=task_semaphore,
            verbose=verbose
        )

    return backup_operation
