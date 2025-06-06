import asyncio
from config import get_config_value, load_config
from enums import CommandType
from rclone import backup
from utils import organize_paths

async def main():
    config = load_config()
    backup_paths: list[str] = get_config_value(config, "backup", "backup_paths")
    remote_name = get_config_value(config, "backup", "remote_name").rstrip("/\\")
    root_dir = get_config_value(config, "backup", "root_dir").rstrip("/\\")
    rclone_args = get_config_value(config, "rclone", "args")
    concurrent_limit = get_config_value(config, "rclone", "concurrent_limit")  
    organized_backup_paths = organize_paths(backup_paths, remote_name, root_dir)

    backup_task_semaphore = asyncio.Semaphore(concurrent_limit)

    _ = await backup(paths=organized_backup_paths, command_type=CommandType.COPY, rclone_args=rclone_args, semaphore=backup_task_semaphore)

if __name__ == "__main__":
    asyncio.run(main())
