from typing import Any


class Command:
    def __init__(
        self,
        kind: str,
        namespace: str,
        name: str,
        key: str | None = None,
    ) -> None:
        self.kind = kind
        self.namespace = namespace
        self.name = name
        self.key = key

    @classmethod
    def from_str(cls, s: str) -> 'Command':
        _, kind, namespace, name, key = s.split('/')
        return cls(
            kind=kind,
            namespace=namespace,
            name=name,
            key=key if key and key != '_' else None,
        )

    @property
    def action(self) -> str:
        return f'/{self.kind}/{self.namespace}/{self.name}/{self.key or "_"}'

    @property
    def search_engine_function_name(self) -> str:
        if self.key:
            return self.key
        return self.name.replace('-', ' ')

    def __eq__(self, other: Any) -> bool:
        return repr(self) == repr(other)

    def __hash__(self) -> int:
        return hash(repr(self))

    def __repr__(self) -> str:
        return f'[{self.namespace}] {self.name.title().replace("-", " ")}'
