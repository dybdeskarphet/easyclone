from typing import TypedDict

class PathItem(TypedDict):
    source: str
    dest: str
    type: str

class SyncStatusItem(PathItem):
    id: str
    status: str
