import asyncio
from types.enums import BackupStatus
from types.models import SyncStatusItem
import uuid

class SyncStatus:
    def __init__(self):
        self.operations: list[SyncStatusItem]  = []
        self.lock: asyncio.Lock = asyncio.Lock()

    async def add_operation(self, source: str, dest: str, path_type: str, status: BackupStatus):
        random_id = str(uuid.uuid4())

        async with self.lock:
            self.operations.append({
                "id": random_id,
                "source": source,
                "dest": dest,
                "status": status.value,
                "type": path_type
            })

        return random_id

    async def delete_operation(self, target_id: str):
        async with self.lock:
            for index, item in enumerate(self.operations):
                if item.get("id") == target_id:
                    del self.operations[index]
                    break;

    async def get_operations(self):
        async with self.lock:
            return self.operations
    
    async def get_operation_count(self):
        async with self.lock:
            return len(self.operations)

sync_status = SyncStatus()
