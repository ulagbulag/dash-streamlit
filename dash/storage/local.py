import base64
import os
from pathlib import Path
import shutil
from typing import Optional, Union

from dash.storage.base import BaseStorage


class LocalStorage(BaseStorage):
    def __init__(self) -> None:
        super().__init__()
        self._base_dir = Path(os.getenv('DASH_DATA_DIR') or './data')
        self._base_dir.mkdir(
            mode=0o700,
            exist_ok=True,
            parents=True,
        )

    def _get_namespaced(self, namespace: str) -> Path:
        path = self._base_dir.joinpath(f'./{namespace}')
        path.mkdir(
            mode=0o700,
            exist_ok=True,
            parents=True,
        )
        return path

    def _get_file(self, namespace: str, key: str) -> Path:
        parent = self._get_namespaced(namespace)
        encoded_key = base64.b64encode(key.encode('utf-8')).decode('utf-8')
        return parent.joinpath(f'./{encoded_key}.csv')

    def list(self, namespace: str) -> list[str]:
        return [
            base64.b64decode(file.name[:-4]).decode('utf-8')
            for file in self._get_namespaced(namespace).iterdir()
            if file.name.endswith('.csv')
        ]

    def get(self, namespace: str, key: str) -> Optional[bytes]:
        path = self._get_file(namespace, key)
        if path.exists():
            with open(path, 'rb') as f:
                return f.read()
        return None

    def set(self, namespace: str, key: str, value: Optional[Union[bytes, str]]) -> None:
        path = self._get_file(namespace, key)
        if isinstance(value, bytes):
            with open(path, 'wb') as f:
                f.write(value)
        elif isinstance(value, str):
            with open(path, 'w') as f:
                f.write(value)
        else:
            if path.exists():
                return os.remove(path)
