from dash.data.object import DashObject
from jsonpointer import set_pointer
from typing import Any


class DynamicObject(DashObject):
    def __init__(self, fields: list[dict[str, Any]]) -> None:
        super().__init__({})
        self._fields = fields

    def fields(self) -> list[dict[str, Any]]:
        return self._fields

    def set(self, key: str, value: Any):
        if value is None:
            return

        key = key[:-1]
        pointer = key.split('/')
        for index in range(1, len(pointer)):
            sub_pointer = pointer[:index + 1]
            sub_key = '/'.join(sub_pointer)
            set_pointer(self.data, sub_key, {}, inplace=True)
        set_pointer(self.data, key, value, inplace=True)
