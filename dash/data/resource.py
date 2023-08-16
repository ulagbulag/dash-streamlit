class ResourceRef:
    def __init__(self, data: dict[str, str]) -> None:
        self.name = data['name']
        self.namespace = data['namespace']

    def __repr__(self) -> str:
        return f'[{self.namespace}] {self.name.title().replace("-", " ")}'
