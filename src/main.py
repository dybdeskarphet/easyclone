import asyncio
from config import get_config_value, load_config
from enums import CommandType, LogLevel
from rclone import backup
from utils import log, organize_paths

async def main():
    config = load_config()
    backup_paths: list[str] = get_config_value(config, "backup", "backup_paths")
    remote_name = get_config_value(config, "backup", "remote_name").rstrip("/\\")
    root_dir = get_config_value(config, "backup", "root_dir").rstrip("/\\")
    rclone_args = get_config_value(config, "rclone", "args")
    organized_backup_paths = organize_paths(backup_paths, remote_name, root_dir)

    _ = await backup(organized_backup_paths, CommandType.COPY, True, rclone_args)

if __name__ == "__main__":
    asyncio.run(main())
