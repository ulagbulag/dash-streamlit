from jsonpointer import resolve_pointer
from typing import Any, Hashable


class DashObject:
    def __init__(self, data: dict[Hashable, Any]) -> None:
        self.data = data

    def name(self) -> str:
        data = resolve_pointer(self.data, '/metadata/name', None)
        if isinstance(data, str) and data:
            return data
        raise Exception('cannot get the name of the object')

    def namespace(self) -> str:
        data = resolve_pointer(self.data, '/metadata/namespace', None)
        if isinstance(data, str) and data:
            return data
        raise Exception('cannot get the namespace of the object')

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
