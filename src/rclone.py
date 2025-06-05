import asyncio

from enums import BackupLog, CommandType, LogLevel
from utils import collapse_user, log

async def backup_command(command_type: CommandType, source: str, dest: str, rclone_args: list[str]):
    cmd = f"rclone {command_type.value} --update --verbose --transfers 30 --checkers 8 --contimeout 60s --timeout 300s --retries 3 --low-level-retries 10 --stats 1s".split()
    cmd += [source, dest]
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()

    stdout = stdout.decode(errors="ignore").strip()
    stderr = stderr.decode(errors="ignore").strip()

    if process.returncode is not None:
        returncode = process.returncode
    else:
        returncode = 0

    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
    }

async def backup(paths: list[dict[str,str]], command_type: CommandType, verbose: bool):
    for path in paths:
        source, dest = path["source"], path["dest"]

        log(f"Backing up {collapse_user(source)}", BackupLog.WAIT)
        stdout, stderr, returncode = (await backup_command(command_type, source, dest)).values()

        if(returncode == 0):
            log(f"Backed up successfully: {collapse_user(source)}", BackupLog.OK)
        else:
            log(f"Back up operation failed: {collapse_user(source)}", BackupLog.ERR)

        if(verbose):
            if(returncode != 0):
                log(f"{stderr}", LogLevel.ERROR)
                log(f"{stdout}", LogLevel.LOG)
            else:
                log(f"{stdout}", LogLevel.LOG)
