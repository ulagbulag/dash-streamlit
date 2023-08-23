import os
from typing import Any

import streamlit as st


class SearchEngine:
    _engine: Any

    def __new__(cls) -> 'SearchEngine':
        @st.cache_resource()
        def init() -> 'SearchEngine':
            client = object.__new__(cls)
            client.__init__()
            return client

        return init()

    def __init__(self) -> None:
        try:
            import hole  # type: ignore[reportMissingImports]
            self._engine = hole.SearchEngine.from_yaml_file(
                path=os.environ.get(
                    'HOLE_SEARCH_ENGINE_PATH',
                    default='./static/search_engine.yaml',
                ),
                add_recommends=True,
            )

            # # Add custom features
            # with open('./static/features.txt', 'r') as f:
            #     features = [
            #         feature.strip()
            #         for feature in f.readlines()
            #         if feature.strip()
            #     ]
            # self._engine.add_category('common', features)
        except ImportError:
            raise ImportError('Cannot find any suitable SearchEngine')

    def __reduce__(self):
        return ()

    def add_function(
        self,
        function: str,
        action: str | None,
        witnesses: list[str] | None,
    ) -> None:
        return self._engine.add_function(
            function=function,
            action=action,
            witnesses=witnesses,
        )

    @st.cache_data(ttl=3600)
    def search(
        self,
        query: str,
        features: list[str] | set[str] | None = None,
    ) -> list[str] | None:
        return self._engine.search(
            query=query,
            features=features,
            force=True,
        )
