import asyncio
from ipc.client import listen_ipc
from ipc.server import start_status_server
from rclone.operations import backup_copy_command, backup_sync_command
import typer

app = typer.Typer()

async def ipc():
    server = await start_status_server()
    async with server:
        await server.serve_forever()

@app.command()
def start_backup():
    async def start():
        task_ipc = asyncio.create_task(ipc())  # runs forever in background
        task_backup = asyncio.create_task(backup_copy_command())
        task_sync = asyncio.create_task(backup_sync_command())

        _ = await asyncio.gather(task_backup, task_sync)
        _ = task_ipc.cancel()

        try:
            await task_ipc
        except asyncio.CancelledError:
            pass
        
    asyncio.run(start())

@app.command()
def read_ipc():
    asyncio.run(listen_ipc())

if __name__ == "__main__":
    app()
