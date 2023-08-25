class SessionRef:
    def __init__(self, data: dict[str, str]) -> None:
        self.namespace = data['namespace']
        self.node_name = data['nodeName']
        self.user_name = data['userName']

    @property
    def novnc_full_url(self) -> str:
        return self._novnc_url(kind='vnc')

    @property
    def novnc_lite_url(self) -> str:
        return self._novnc_url(kind='vnc_lite')

    def _novnc_url(self, kind: str) -> str:
        return f'https://mobilex.kr/dashboard/vnc/{kind}.html?host=mobilex.kr/user/{self.user_name}/vnc/&scale=true'

    def to_dict(self) -> dict[str, str]:
        return {
            'Name': self.user_name,
            'Namespace': self.namespace,
            'NodeName': self.node_name,
        }

    def __repr__(self) -> str:
        return self.user_name
