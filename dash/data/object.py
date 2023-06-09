from jsonpointer import resolve_pointer
from typing import Any


class DashObject:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def title(self) -> str:
        name = '???'
        for pointer in [
            '/metadata/labels/dash.ulagbulag.io~1alias',
            '/metadata/name',
        ]:
            data = resolve_pointer(self.data, pointer, None)
            if isinstance(data, str) and data:
                name = data
                break

        return name.title().replace('-', ' ')
