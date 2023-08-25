from typing import Any, Hashable
import pandas as pd
import streamlit as st


@st.cache_data()
def to_dataframe(
    *,
    items: list[dict[Hashable, Any]],
    map: list[tuple[str, str, bool]] = [
        ('name', '/metadata/name/', False),
        ('state', '/status/state/', False),
        ('created at', '/metadata/creationTimestamp/', False),
        ('updated at', '/status/lastUpdated/', False),
    ],
) -> pd.DataFrame:
    map_splited = [
        (renamed.title(), origin.split('/'), is_title)
        for renamed, origin, is_title in map
    ]

    def get_jq_style(data, keys: list[str], is_title: bool):
        if not keys:
            if is_title:
                return str(data).title().replace('-', ' ')
            return data

        key = keys[0].replace('~0', '~').replace('~1', '/')
        if not key:
            return get_jq_style(data, keys[1:], is_title)

        if data is None or key not in data:
            return None
        return get_jq_style(data[key], keys[1:], is_title)

    return pd.DataFrame.from_dict({
        renamed: [
            get_jq_style(item, origin, is_title)
            for item in items
        ]
        for renamed, origin, is_title in map_splited
    })
