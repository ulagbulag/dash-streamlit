from abc import abstractmethod, ABCMeta
from typing import Optional, Union


class BaseStorage(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    def namespaced(self, namespace: str):
        return NamespacedStorage(self, namespace)

    @abstractmethod
    def list(self, namespace: str) -> list[str]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, namespace: str, key: str) -> Optional[bytes]:
        raise NotImplementedError()

    @abstractmethod
    def set(self, namespace: str, key: str, value: Optional[Union[bytes, str]]) -> None:
        raise NotImplementedError()


class NamespacedStorage:
    def __init__(self, storage: BaseStorage, namespace: str) -> None:
        self._storage = storage
        self._namespace = namespace

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def list(self) -> list[str]:
        return self._storage.list(self._namespace)

    def get(self, key: str) -> Optional[bytes]:
        return self._storage.get(self._namespace, key)

    def set(self, key: str, value: Optional[Union[bytes, str]]) -> None:
        return self._storage.set(self._namespace, key, value)
