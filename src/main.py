import asyncio
from config import load_config
from enums import CommandType
from ipc.server import start_status_server
from rclone.backup import backup
from utils import organize_paths

async def main():
    _server = await start_status_server()
    config = load_config()
    copy_paths = organize_paths(config.backup.copy_paths, config.backup.remote_name, config.backup.root_dir)
    # sync_paths = organize_paths(config.backup.sync_paths, config.backup.remote_name, config.backup.root_dir)
    backup_task_semaphore = asyncio.Semaphore(config.rclone.concurrent_limit)

    _ = await backup(paths=copy_paths, command_type=CommandType.COPY, rclone_args=config.rclone.args, semaphore=backup_task_semaphore)

if __name__ == "__main__":
    asyncio.run(main())
