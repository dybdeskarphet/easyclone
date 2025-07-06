import asyncio
import json
from pathlib import Path
from easyclone.utypes.enums import LogLevel
from easyclone.shared import sync_status
from easyclone.utils.essentials import log

SOCKET_PATH = "/tmp/easyclone.sock"

async def handle_client(_reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    try:
        while True:
            message = json.dumps({
                "total_path_count": await sync_status.get_total_path(),
                "finished_path_count": await sync_status.get_currently_finished(),
                "empty_paths": await sync_status.get_empty_paths(),
                "operation_count": await sync_status.get_operation_count(),
                "operations": await sync_status.get_operations()
            }).encode() + b"\n"

            writer.write(message)

            await writer.drain()
            await asyncio.sleep(0.5)
    except (ConnectionResetError, BrokenPipeError, asyncio.IncompleteReadError):
        pass
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except BrokenPipeError:
            pass

async def start_status_server():
    try:
        Path(SOCKET_PATH).unlink()
    except FileNotFoundError as e:
        pass
    except Exception as e:
        log(f"Something happened while connecting to the socket for status server: {e}", LogLevel.ERROR)
        raise

    try:
        server = await asyncio.start_unix_server(handle_client, path=SOCKET_PATH)
    except Exception as e:
        log(f"Couldn't create the UNIX server: {e}", LogLevel.ERROR)
        raise

    return server
