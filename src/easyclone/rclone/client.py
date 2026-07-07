from datetime import datetime, timedelta
import asyncio
import re
from multiprocessing import process
import shlex
import subprocess
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

        timestamp = datetime.now().strftime(cfg.backup.versioning.timestamp)
        remote = cfg.backup.versioning.remote_name
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


async def prune_archives_by_folder(
    remote: str,
    archive_path: str,
    prune_timeout: str,
    timestamp_format: str,
    rclone_args: list[str],
    verbose: bool = False,
):
    match = re.match(r"^(\d+)([dhms])$", prune_timeout.strip())
    if not match:
        log(f"Invalid prune_timeout format: {prune_timeout}", BackupLog.ERR)
        return

    value, unit = int(match.group(1)), match.group(2)
    delta_map = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}
    cutoff_date = datetime.now() - timedelta(**{delta_map[unit]: value})

    all_args: list[str] = []
    for arg in rclone_args:
        all_args.extend(shlex.split(arg))

    filtered_args = []
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

    purge_args = []
    skip_val = False
    for arg in filtered_args:
        if skip_val:
            skip_val = False
            continue
        if arg in (
            "--exclude",
            "--exclude-from",
            "--include",
            "--include-from",
            "--filter",
            "--filter-from",
        ):
            skip_val = True
            continue
        if arg.startswith(("--exclude=", "--include=", "--filter=")):
            continue
        purge_args.append(arg)

    archive_dest = f"{remote}:{archive_path}"

    list_cmd = ["rclone", "lsf", "--dirs-only", archive_dest] + filtered_args
    process = await asyncio.create_subprocess_exec(
        *list_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        return

    folders = stdout.decode(errors="ignore").strip().split("\n")

    for folder in folders:
        folder = folder.strip("/")
        if not folder:
            continue

        try:
            folder_date = datetime.strptime(folder, timestamp_format)
            if folder_date < cutoff_date:
                log(f"Purging expired archive folder: {folder}...", BackupLog.WAIT)
                purge_cmd = ["rclone", "purge", f"{archive_dest}/{folder}"] + purge_args
                process_purge = await asyncio.create_subprocess_exec(
                    *purge_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout_p, stderr_p = await process_purge.communicate()

                if process_purge.returncode == 0:
                    log(
                        f"Purged expired archive folder successfully: {folder}",
                        BackupLog.OK,
                    )
                else:
                    log(
                        f"Failed to purge folder {folder}: {stderr_p.decode(errors='ignore').strip()}",
                        BackupLog.ERR,
                    )

                if verbose:
                    if stdout_p:
                        log(stdout_p.decode(errors="ignore").strip(), LogLevel.LOG)
        except ValueError:
            continue
