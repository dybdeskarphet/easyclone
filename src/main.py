import asyncio
from typing import Any
from config import config
from ipc.client import listen_ipc
from ipc.server import start_status_server
from rclone.operations import backup_copy_operation, backup_sync_operation
import typer
import json

from shared import sync_status

app = typer.Typer()

async def ipc():
    server = await start_status_server()
    async with server:
        await server.serve_forever()

@app.command()
def start_backup(verbose: bool = False):
    async def start():
        await sync_status.set_total_path_count(len(config.backup.sync_paths) + len(config.backup.copy_paths))

        _ipc_task = asyncio.create_task(ipc()) 

        verbose_state = verbose or config.backup.verbose_log

        await backup_copy_operation(verbose_state)
        await backup_sync_operation(verbose_state)

    asyncio.run(start())

@app.command()
def get_status(all: bool = False, show_total: bool = False, show_current: bool = False, show_operations: bool = False):
    data: Any = asyncio.run(listen_ipc())

    if show_total:
        print(data["total_path_count"])

    if show_current:
        print(data["operation_count"])

    if show_operations:
        print(json.dumps(data["operations"], indent=2))

    if all:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    app()
