import os
from typing import Any

import requests
import streamlit as st

from dash.data.function import DashFunction


class DashClient:
    def __new__(cls) -> 'DashClient':
        @st.cache_resource()
        def init() -> 'DashClient':
            client = object.__new__(cls)
            client.__init__()
            return client

        return init()

    def __init__(self) -> None:
        self._session = requests.Session()
        self._host = os.environ.get(
            'DASH_HOST') or 'http://gateway.dash.svc.ops.openark'

    def _call_raw(self, *, method: str, path: str, value: Any = None) -> Any:
        response = self._session.request(
            method=method,
            url=f'{self._host}{path}',
            json=value,
        )

        data = response.json() if response.text else {}
        if response.status_code == 200:
            if 'spec' in data:
                return data['spec']
            raise Exception(f'Failed to execute {path}: no output')
        if 'spec' in data:
            raise Exception(f'Failed to execute {path}: {data["spec"]}')
        raise Exception(
            f'Failed to execute {path}: status code [{response.status_code}]')

    def get_function(self, *, name: str) -> DashFunction:
        return DashFunction(
            name=name,
            data=self._call_raw(
                method='GET',
                path=f'/function/{name}/',
            ),
        )

    def get_function_list(self) -> list[str]:
        return self._call_raw(
            method='GET',
            path=f'/function/',
        )

    def post_function(self, *, name: str, value: Any):
        self._call_raw(
            method='POST',
            path=f'/function/{name}/',
            value=value,
        )

    def get_model(self, *, name: str) -> dict:
        return self._call_raw(
            method='GET',
            path=f'/model/{name}/',
        )

    def get_model_function_list(self, *, name: str) -> list[dict[str, Any]]:
        return self._call_raw(
            method='GET',
            path=f'/model/{name}/function/',
        )

    def get_model_list(self) -> list[str]:
        return self._call_raw(
            method='GET',
            path=f'/model/',
        )

    def get_model_item(self, *, name: str, item: str) -> list[dict[str, Any]]:
        return self._call_raw(
            method='GET',
            path=f'/model/{name}/item/{item}/',
        )

    def get_model_item_list(self, *, name: str) -> list[dict[str, Any]]:
        return self._call_raw(
            method='GET',
            path=f'/model/{name}/item/',
        )
