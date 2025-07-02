import asyncio
from typing import Any
from config import load_config
from ipc.client import listen_ipc
from ipc.server import start_status_server
from rclone.operations import backup_copy_command, backup_sync_command
import typer
import json

from shared import sync_status

app = typer.Typer()

async def ipc():
    server = await start_status_server()
    async with server:
        await server.serve_forever()

@app.command()
def start_backup():
    async def start():
        config = load_config()
        await sync_status.set_total_path_count(len(config.backup.sync_paths) + len(config.backup.copy_paths))
        task_ipc = asyncio.create_task(ipc())  # runs forever in background
        task_backup = asyncio.create_task(backup_copy_command())
        task_sync = asyncio.create_task(backup_sync_command())

        _ = await asyncio.gather(task_backup, task_sync)
        _ = task_ipc.cancel()

        try:
            await task_ipc
        except asyncio.CancelledError:
            pass
        
    asyncio.run(start())

@app.command()
def get_status(all: bool = False, show_total: bool = False, show_current: bool = False, show_operations: bool = False):
    data: Any = asyncio.run(listen_ipc())

    if show_total:
        print(data.total_paths)

    if show_current:
        print(data.operation_count)

    if show_operations:
        print(json.dumps(data.operations, indent=2))

    if all:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    app()
