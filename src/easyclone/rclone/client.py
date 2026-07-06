from datetime import datetime
import asyncio
import shlex
from easyclone.config import cfg
from easyclone.core.state import sync_status
from easyclone.core.types import (
    BackupLog,
    BackupStatus,
    CommandType,
    LogLevel,
    RcloneOperationType,
    PathItem,
)
from easyclone.utils.logging import log
from easyclone.utils.path import collapseuser


async def backup_command(
    rclone_command: list[str],
    source: str,
    dest: str,
    path_type: str,
    command_type: CommandType,
    task_backup_dir: str,
    verbose: bool = False,
):
    cmd = rclone_command + [source, dest]
    operation_name = command_type.value.capitalize() + "ing"

    log(f"{operation_name} {collapseuser(source)}", BackupLog.WAIT)
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    if task_backup_dir.strip():
        log(
            f"Archiving the old version of {collapseuser(source)} to {task_backup_dir}",
            BackupLog.WAIT,
        )

    process_id = await sync_status.add_operation(
        source=source,
        dest=dest,
        path_type=path_type,
        status=BackupStatus.IN_PROGRESS,
        operation_type=RcloneOperationType.BACKUP,
    )

    stdout, stderr = await process.communicate()
    stdout = stdout.decode(errors="ignore").strip()
    stderr = stderr.decode(errors="ignore").strip()

    collapsed_source = collapseuser(source)
    match process.returncode:
        case 0:
            log(f"Backed up successfully: {collapsed_source}", BackupLog.OK)
        case 1:
            log(f"Back up operation failed: {collapsed_source}", BackupLog.ERR)
        case _:
            log(
                f"Back up operation failed with {process.returncode} exit code: {collapsed_source}",
                BackupLog.ERR,
            )

    await sync_status.delete_operation(process_id)
    await sync_status.add_currently_finished()

    if verbose:
        if stderr:
            log(f"{stderr}", LogLevel.WARN)
        if stdout:
            log(f"{stdout}", LogLevel.LOG)


async def backup(
    paths: list[PathItem],
    command_type: CommandType,
    rclone_args: list[str],
    semaphore: asyncio.Semaphore,
    verbose: bool = False,
):
    cmd = ["rclone", command_type.value]

    all_args: list[str] = []
    for arg in rclone_args:
        all_args.extend(shlex.split(arg))

    remote = None
    timestamp = None
    filtered_args: list[str] = []
    if cfg.backup.versioning.enable:
        skip_next = False
        for arg in all_args:
            if skip_next:
                skip_next = False
                continue

            if arg.startswith("--backup-dir="):
                continue

            if arg == "--backup-dir":
                skip_next = True
                continue

            filtered_args.append(arg)

        remote = cfg.backup.versioning.remote_name
        timestamp = datetime.now().strftime(cfg.backup.versioning.timestamp)
        if not remote or not remote.strip():
            remote = cfg.backup.remote_name
    else:
        filtered_args = all_args

    cmd += filtered_args

    # I have to do this because python doesn't have anon coroutines
    async def backup_task(source: str, dest: str, path_type: str):
        cmd_for_task = cmd.copy()
        task_backup_dir = ""
        if cfg.backup.versioning.enable:
            dest_prefix = f"{cfg.backup.remote_name}:{cfg.backup.root_dir}".strip("/")
            archive_prefix = f"{remote}:{cfg.backup.versioning.path}/{timestamp}"
            task_backup_dir = dest.replace(dest_prefix, archive_prefix)
            cmd_for_task += ["--backup-dir", task_backup_dir]

        async with semaphore:
            await backup_command(
                rclone_command=cmd_for_task,
                source=source,
                dest=dest,
                path_type=path_type,
                command_type=command_type,
                task_backup_dir=task_backup_dir,
                verbose=verbose,
            )

    tasks = [
        backup_task(path["source"], path["dest"], path["path_type"]) for path in paths
    ]

    return await asyncio.gather(*tasks)
