import asyncio
from typing import Annotated, Any
from easyclone.config import cfg
from easyclone.ipc.client import listen_ipc
from easyclone.ipc.server import start_status_server
from easyclone.rclone.operations import make_backup_operation
import typer
import json
from easyclone.shared import sync_status
from easyclone.utils.essentials import exit_if_currently_running, exit_if_no_rclone
from easyclone.utypes.enums import CommandType


app = typer.Typer(
    help="Very convenient Rclone bulk backup wrapper",
    context_settings={"help_option_names": ["-h", "--help"]},
)


async def ipc():
    server = await start_status_server()
    async with server:
        await server.serve_forever()


@app.command(help="Starts the backup process using the details in the config file.")
def start_backup(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v", help="Enables the rclone logging (overrides config)."
        ),
    ] = False,
):
    async def start():
        exit_if_no_rclone()
        exit_if_currently_running()
        await sync_status.set_total_path_count(
            len(cfg.backup.sync_paths) + len(cfg.backup.copy_paths)
        )

        _ipc_task = asyncio.create_task(ipc())

        verbose_state = verbose or cfg.backup.verbose_log

        await make_backup_operation(
            CommandType.COPY, cfg.backup.copy_paths, verbose_state
        )()
        await make_backup_operation(
            CommandType.SYNC, cfg.backup.sync_paths, verbose_state
        )()

    asyncio.run(start())


@app.command(help="Gets status information about the backup process.")
def get_status(
    all_args: Annotated[
        bool,
        typer.Option("--all", "-a", help="Show all the backup status information."),
    ] = False,
    show_total: Annotated[
        bool, typer.Option("--show-total", "-t", help="Show the total amount of paths.")
    ] = False,
    show_current: Annotated[
        bool,
        typer.Option(
            "--show-current", "-c", help="Show the total amount of pending paths."
        ),
    ] = False,
    show_operations: Annotated[
        bool,
        typer.Option(
            "--show-operations", "-o", help="Show currently running operations."
        ),
    ] = False,
    show_finished_path_count: Annotated[
        bool,
        typer.Option(
            "--show-finished", "-f", help="Show the total amount of finished paths."
        ),
    ] = False,
    show_operation_count: Annotated[
        bool,
        typer.Option(
            "--get-operation-count",
            "-O",
            help="Show the total amount of running operations.",
        ),
    ] = False,
    show_empty_paths: Annotated[
        bool, typer.Option("--show-empty-paths", "-e", help="Show all the empty paths.")
    ] = False,
):
    data: Any = asyncio.run(listen_ipc())

    args = [
        show_total,
        show_current,
        show_operations,
        show_operation_count,
        show_finished_path_count,
        show_empty_paths,
    ]

    if not any(args) or all_args:
        print(json.dumps(data, indent=2))
        return

    if show_total:
        print(data["total_path_count"])

    if show_current:
        print(data["operation_count"])

    if show_operations:
        print(json.dumps(data["operations"], indent=2))

    if show_operation_count:
        print(data["operation_count"])

    if show_finished_path_count:
        print(data["finished_path_count"])

    if show_empty_paths:
        print(data["empty_paths"])


if __name__ == "__main__":
    app()
