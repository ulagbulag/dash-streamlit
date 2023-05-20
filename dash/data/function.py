from jsonpointer import resolve_pointer
from typing import Any


class DashFunction:
    def __init__(self, name: str, data: dict[str, Any]) -> None:
        self.name = name
        self.data = data

    def title(self) -> str:
        name = self.name
        for pointer in [
            '/metadata/labels/dash.ulagbulag.io~1alias',
            '/metadata/name',
        ]:
            data = resolve_pointer(self.data, pointer, None)
            if isinstance(data, str) and data:
                name = data
                break

        return name.title().replace('-', ' ')
