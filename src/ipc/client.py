import asyncio
import json

from utils import log
from utypes.enums import LogLevel

SOCKET_PATH = "/tmp/syncgdrive.sock"

async def listen_ipc():
    try:
        reader, writer = await asyncio.open_unix_connection(SOCKET_PATH)
    except (FileNotFoundError, ConnectionRefusedError):
        log("No tasks are running at the moment.", LogLevel.ERROR)
        exit(1)

    try:
        line = await reader.readline()
        if not line:
            log("No tasks are running at the moment", LogLevel.ERROR)
            exit(1)

        data = json.loads(line.decode())
        return data
    finally:
        writer.close()
        await writer.wait_closed()
