import asyncio
from asyncio.tasks import Task
import shlex

from enums import BackupLog, BackupStatus, CommandType, LogLevel
from ipc.server import handle_client, start_status_server
from utils import collapseuser, log
from shared.sync_status import sync_status

async def backup_command(command_type: CommandType, source: str, dest: str, rclone_args: list[str], verbose: bool = False):
    """
    Used for individual backup requests.
    It's not intended to used by itself.
    Use the backup() function instead.
    """
    cmd = f"rclone {command_type.value}".split() + [source,dest]
    cmd += [part for arg in rclone_args for part in shlex.split(str(arg))]
    log(f"Backing up {collapseuser(source)}", BackupLog.WAIT)
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    process_id = await sync_status.add_operation(source, dest, BackupStatus.IN_PROGRESS)

    stdout, stderr = await process.communicate()

    stdout = stdout.decode(errors="ignore").strip()
    stderr = stderr.decode(errors="ignore").strip()

    _ = await process.wait()

    match process.returncode:
        case 0:
            log(f"Backed up successfully: {collapseuser(source)}", BackupLog.OK)
        case 1:
            log(f"Back up operation failed: {collapseuser(source)}", BackupLog.ERR)
        case _:
            log(f"Back up operation failed with {process.returncode} exit code: {collapseuser(source)}", BackupLog.ERR)

    await sync_status.delete_operation(process_id)

    if verbose:
        if stderr: 
            log(f"{stderr}", LogLevel.WARN)
        if stdout:
            log(f"{stdout}", LogLevel.LOG)

async def backup(paths: list[dict[str,str]], command_type: CommandType, verbose: bool, rclone_args: list[str], semaphore: asyncio.Semaphore):
    """
    The main function that runs the backup task.
    """
    tasks: list[Task[None]] = []
    _ = await start_status_server()

    for path in paths:
        source, dest = path["source"], path["dest"]

        async def backup_task(source: str = source, dest: str = dest):
            async with semaphore:
                await backup_command(command_type, source, dest, rclone_args, verbose)

        task = asyncio.create_task(backup_task())
        tasks.append(task)

    _ = await asyncio.gather(*tasks)
