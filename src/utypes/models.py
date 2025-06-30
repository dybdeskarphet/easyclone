from typing import TypedDict

class PathItem(TypedDict):
    source: str
    dest: str
    path_type: str

class SyncStatusItem(PathItem):
    id: str
    status: str
    operation_type: str
