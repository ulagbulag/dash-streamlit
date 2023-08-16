
from typing import Any, Hashable


class User:
    def __init__(self, data: dict[Hashable, Any]) -> None:
        self.data = data

    def get_box_name(self) -> str | None:
        return self.data.get('boxName')

    def get_namespace(self) -> str:
        return str(self.data['namespace'])

    def get_nickname(self) -> str:
        return str(self.data['user']['name'])

    def get_user_name(self) -> str:
        return str(self.data['userName'])

    def get_role_admin(self) -> bool:
        return bool(self.data['role']['isAdmin'])

    def get_role_dev(self) -> bool:
        return bool(self.data['role']['isDev'])

    def get_role_ops(self) -> bool:
        return bool(self.data['role']['isOps'])
