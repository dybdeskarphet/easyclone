import asyncio
from easyclone.utypes.enums import BackupStatus, RcloneOperationType
from easyclone.utypes.models import SyncStatusItem
import uuid

class SyncStatus:
    def __init__(self):
        self.total_path_count: int = 0
        self.operations: list[SyncStatusItem]  = []
        self.lock: asyncio.Lock = asyncio.Lock()
        self.finished_path_count: int = 0

    async def add_operation(self, source: str, dest: str, path_type: str, status: BackupStatus, operation_type: RcloneOperationType):
        random_id = str(uuid.uuid4())

        async with self.lock:
            self.operations.append({
                "id": random_id,
                "source": source,
                "dest": dest,
                "status": status.value,
                "path_type": path_type,
                "operation_type": operation_type.value
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

    async def set_total_path_count(self, count: int):
        async with self.lock:
            self.total_path_count = count

    async def reset_total_paths(self):
        async with self.lock:
            self.total_path_count = 0

    async def get_total_path(self):
        async with self.lock:
            return self.total_path_count

    async def add_currently_finished(self):
        async with self.lock:
            self.finished_path_count += 1

    async def get_currently_finished(self):
        async with self.lock:
            return self.finished_path_count
