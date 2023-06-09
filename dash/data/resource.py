class ResourceRef:
    def __init__(self, data: dict[str, str]) -> None:
        self.name = data['name']
        self.namespace = data['namespace']
