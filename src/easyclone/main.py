import asyncio
from typing import Annotated, Any
from easyclone.config import cfg
from easyclone.ipc.client import listen_ipc
from easyclone.ipc.server import start_status_server
from easyclone.rclone.operations import backup_copy_operation, backup_sync_operation
import typer
import json

from easyclone.shared import sync_status

app = typer.Typer(
    help="Very convenient Rclone bulk backup wrapper",
    context_settings={"help_option_names": ["-h", "--help"]}
)

async def ipc():
    server = await start_status_server()
    async with server:
        await server.serve_forever()

@app.command(help="Starts the backup process using the details in the config file.")
def start_backup(verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enables the rclone logging (overrides config).")] = False):
    async def start():
        await sync_status.set_total_path_count(len(cfg.backup.sync_paths) + len(cfg.backup.copy_paths))

        _ipc_task = asyncio.create_task(ipc()) 

        verbose_state = verbose or cfg.backup.verbose_log

        await backup_copy_operation(verbose_state)
        await backup_sync_operation(verbose_state)

    asyncio.run(start())

@app.command(help="Gets status information about the backup process.")
def get_status(
        all: Annotated[bool, typer.Option("--all", "-a", help="Show all the backup status information.")] = False,
        show_total: Annotated[bool, typer.Option("--show-total", "-t", help="Show the total amount of paths.")] = False,
        show_current: Annotated[bool, typer.Option("--show-current", "-c", help="Show the total amount of pending paths.")] = False,
        show_operations: Annotated[bool, typer.Option("--show-operations", "-o", help="Show currently running operations.")] = False
):
    data: Any = asyncio.run(listen_ipc())

    if (not show_total and not show_current and not show_operations or all) or (show_total and show_current and show_operations):
        print(json.dumps(data, indent=2))
        return

    if show_total:
        print(data["total_path_count"])

    if show_current:
        print(data["operation_count"])

    if show_operations:
        print(json.dumps(data["operations"], indent=2))

if __name__ == "__main__":
    app()
