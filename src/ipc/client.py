import asyncio
import json

SOCKET_PATH = "/tmp/syncgdrive.sock"

async def listen():
    reader, writer = await asyncio.open_unix_connection(SOCKET_PATH)
    while True:
        line = await reader.readline()
        if not line:
            break
        data = json.loads(line.decode())
        print("Status update:", json.dumps(data, indent=2))

asyncio.run(listen())

