import os
from typing import Any

import requests
import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

from dash.data.function import DashFunction
from dash.data.model import DashModel


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
        self._host = os.environ.get('DASH_HOST') \
            or 'https://mobilex.kr/dash/api/'

    def _call_raw(
        self, *, namespace: str | None = None,
        method: str, path: str, value: Any = None,
    ) -> Any:
        headers = _get_websocket_headers() or {}
        headers_pass_through = [
            'Authorization',
            'Cookie',
        ]

        headers = {
            header: headers.get(header, None)
            for header in headers_pass_through
        }
        if namespace:
            headers['X-ARK-NAMESPACE'] = namespace

        response = self._session.request(
            method=method,
            url=f'{self._host}{path}',
            headers=headers,
            json=value,
        )

        if response.text:
            data = response.json()
        else:
            raise Exception(f'Failed to execute {path}: no response')

        if response.status_code == 200:
            if 'spec' in data:
                return data['spec']
            raise Exception(f'Failed to execute {path}: no output')
        if 'spec' in data:
            raise Exception(f'Failed to execute {path}: {data["spec"]}')
        raise Exception(
            f'Failed to execute {path}: status code [{response.status_code}]')

    def get_function(
        self, *, namespace: str | None = None,
        name: str,
    ) -> DashFunction:
        return DashFunction(
            data=self._call_raw(
                namespace=namespace,
                method='GET',
                path=f'/function/{name}/',
            ),
        )

    def get_function_list(
        self, *, namespace: str | None = None,
    ) -> list[Any]:
        return self._call_raw(
            namespace=namespace,
            method='GET',
            path=f'/function/',
        )

    def post_function(
        self, *, namespace: str | None = None,
        name: str, value: Any,
    ):
        self._call_raw(
            namespace=namespace,
            method='POST',
            path=f'/function/{name}/',
            value=value,
        )

    def get_model(
        self, *, namespace: str | None = None,
        name: str,
    ) -> dict:
        return self._call_raw(
            namespace=namespace,
            method='GET',
            path=f'/model/{name}/',
        )

    def get_model_function_list(
        self, *, namespace: str | None = None,
        name: str,
    ) -> list[dict[str, Any]]:
        return self._call_raw(
            namespace=namespace,
            method='GET',
            path=f'/model/{name}/function/',
        )

    def get_model_list(
        self, *, namespace: str | None = None,
    ) -> list[Any]:
        return self._call_raw(
            namespace=namespace,
            method='GET',
            path=f'/model/',
        )

    def get_model_item(
        self, *, namespace: str | None = None,
        name: str, item: str,
    ) -> DashModel:
        return DashModel(
            data=self._call_raw(
                namespace=namespace,
                method='GET',
                path=f'/model/{name}/item/{item}/',
            ),
        )

    def get_model_item_list(
        self, *, namespace: str | None = None,
        name: str,
    ) -> list[DashModel]:
        return [
            DashModel(
                data=data,
            )
            for data in self._call_raw(
                namespace=namespace,
                method='GET',
                path=f'/model/{name}/item/',
            )
        ]
