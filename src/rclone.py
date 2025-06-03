import asyncio
import subprocess

from enums import CommandType

async def backup_command(command_type: CommandType, source: str, dest: str):
    cmd = f"rclone {command_type.value} --update --verbose --transfers 30 --checkers 8 --contimeout 60s --timeout 300s --retries 3 --low-level-retries 10 --stats 1s".split()
    cmd += [source, dest]
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()


# def backup(paths: list[dict[str,str]]):
