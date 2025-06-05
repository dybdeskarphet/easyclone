import asyncio
from asyncio.tasks import Task
import shlex

from enums import BackupLog, CommandType, LogLevel
from utils import collapse_user, log

async def backup_command(command_type: CommandType, source: str, dest: str, rclone_args: list[str], verbose: bool = False):
    cmd = f"rclone {command_type.value}".split()
    cmd += [source, dest]
    cmd += [part for arg in rclone_args for part in shlex.split(str(arg))]
    log(f"Backing up {collapse_user(source)}", BackupLog.WAIT)
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()

    stdout = stdout.decode(errors="ignore").strip()
    stderr = stderr.decode(errors="ignore").strip()

    _ = await process.wait()

    if process.returncode == 0:
        log(f"Backed up successfully: {collapse_user(source)}", BackupLog.OK)
    elif process.returncode == 1:
        log(f"Back up operation failed: {collapse_user(source)}", BackupLog.ERR)
    else:
        log(f"Back up operation failed with {process.returncode} exit code: {collapse_user(source)}", BackupLog.ERR)

    if(verbose):
        if stderr != "":
            log(f"{stderr}", LogLevel.WARN)

        if stdout != "":
            log(f"{stdout}", LogLevel.LOG)

async def backup(paths: list[dict[str,str]], command_type: CommandType, verbose: bool, rclone_args: list[str]):
    tasks: list[Task[None]] = []

    for path in paths:
        source, dest = path["source"], path["dest"]
        task = asyncio.create_task(backup_command(command_type, source, dest, rclone_args, verbose))
        tasks.append(task)

    _ = await asyncio.gather(*tasks)
