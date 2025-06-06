import asyncio
import json
from pathlib import Path
from shared import sync_status
from utypes.enums import LogLevel
from utils import log

SOCKET_PATH = "/tmp/syncgdrive.sock"

async def handle_client(_reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    try:
        while True:
            message = json.dumps({
                "operation_count": await sync_status.get_operation_count(),
                "operations": await sync_status.get_operations()
            }).encode() + b"\n"

            writer.write(message)

            await writer.drain()
            await asyncio.sleep(0.5)
    except Exception as e:
        raise e
    finally:
        writer.close()
        await writer.wait_closed()

async def start_status_server():
    try:
        Path(SOCKET_PATH).unlink()
    except FileNotFoundError:
        pass
    except Exception as e:
        log(f"Something happened while connecting to the socket for status server: {e}", LogLevel.ERROR)

    server = await asyncio.start_unix_server(handle_client, path=SOCKET_PATH)

    return server
