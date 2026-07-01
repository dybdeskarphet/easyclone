import asyncio
import sys
from typing import Annotated, Any
from easyclone.config import cfg
from easyclone.ipc.client import listen_ipc
from easyclone.ipc.server import start_status_server
from easyclone.rclone.operations import make_backup_operation
from easyclone.utils.path import collapseuser, find_missing
import typer
import json
from easyclone.shared import sync_status
from easyclone.utils.essentials import exit_if_currently_running, exit_if_no_rclone
from easyclone.utypes.enums import CommandType, FindMissingOptions

app = typer.Typer(
    help="Very convenient Rclone bulk backup wrapper",
    context_settings={"help_option_names": ["-h", "--help"]},
)


async def ipc():
    server = await start_status_server()
    async with server:
        await server.serve_forever()


async def _run_backup_operations(verbose_state: bool):
    await sync_status.reset_all()
    await sync_status.set_total_path_count(
        len(cfg.backup.sync_paths) + len(cfg.backup.copy_paths)
    )

    await make_backup_operation(
        CommandType.COPY, cfg.backup.copy_paths, verbose_state
    )()
    await make_backup_operation(
        CommandType.SYNC, cfg.backup.sync_paths, verbose_state
    )()


def _setup_environment():
    import atexit
    from os import path, remove
    import signal
    from types import FrameType
    from easyclone.ipc.client import SOCKET_PATH
    from easyclone.utils.essentials import log
    from easyclone.utypes.enums import LogLevel

    def cleanup():
        if path.exists(SOCKET_PATH):
            log("Cleaning up socket file...", LogLevel.WARN)
            remove(SOCKET_PATH)

    _ = atexit.register(cleanup)

    def handle_signal(_signum: int, _frame: FrameType | None):
        cleanup()
        sys.exit(0)

    _ = signal.signal(signal.SIGINT, handle_signal)
    _ = signal.signal(signal.SIGTERM, handle_signal)


@app.command(help="Starts the backup process using the details in the config file.")
def start_backup(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v", help="Enables the rclone logging (overrides config)."
        ),
    ] = False,
):
    exit_if_currently_running()
    _setup_environment()

    async def start():
        exit_if_no_rclone()

        _ipc_task = asyncio.create_task(ipc())

        verbose_state = verbose or cfg.backup.verbose_log
        await _run_backup_operations(verbose_state)

    asyncio.run(start())


@app.command(help="Starts the backup process as a daemon that runs periodically.")
def daemon(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v", help="Enables the rclone logging (overrides config)."
        ),
    ] = False,
):
    exit_if_currently_running()
    _setup_environment()

    async def start():
        from easyclone.utils.essentials import log
        from easyclone.utypes.enums import LogLevel

        exit_if_no_rclone()

        _ipc_task = asyncio.create_task(ipc())

        verbose_state = verbose or cfg.backup.verbose_log

        interval_minutes = cfg.daemon.interval
        interval_seconds = interval_minutes * 60
        countdown = cfg.daemon.countdown

        while True:
            await _run_backup_operations(verbose_state)

            if countdown:
                for remaining in range(interval_seconds, 0, -1):
                    sys.stdout.write(
                        f"\rWaiting for the next backup for {remaining // 60}m {remaining % 60}s... "
                    )
                    sys.stdout.flush()
                    await asyncio.sleep(1)
                sys.stdout.write("\r" + " " * 80 + "\r")
                sys.stdout.flush()
            else:
                log(
                    f"Waiting for the next backup for {interval_minutes} minutes...",
                    LogLevel.LOG,
                )
                await asyncio.sleep(interval_seconds)

    asyncio.run(start())


@app.command(
    help="Lists the directories and files that are not getting synced or backed up"
)
def get_missing(
    recursive: Annotated[
        bool, typer.Option("--recursive", "-r", help="Recurse into directories")
    ] = False,
    list: Annotated[
        FindMissingOptions,
        typer.Option("--list", "-l", help="Select the list you want to filter from"),
    ] = FindMissingOptions.all,
    want_json: Annotated[
        bool, typer.Option("--json", "-j", help="Show the output in JSON format")
    ] = False,
):
    missing = find_missing(recursive=recursive, list_type=list)

    if want_json:
        print(json.dumps(missing, indent=2))
    else:
        [print(collapseuser(p)) for p in missing]


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
