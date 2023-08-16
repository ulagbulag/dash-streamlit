import streamlit as st

from dash.data.resource import ResourceRef
from dash.data.user import User
from dash.home.command import draw_page as _draw_page_command
from dash.home.favorite import draw_page as _draw_page_favorite
from dash.home.me import draw_page as _draw_page_me


def draw_page(
    *, functions: dict[str, list[ResourceRef]],
    user: User,
) -> None:
    # Page Information
    st.title('Welcome to OpenARK Dashboard')

    # Draw command line widget
    _draw_page_command(
        functions=functions,
        user=user,
    )
    st.divider()

    # Compose home page widgets
    column_favorites, column_me = st.columns(2)

    # Draw "Favorites" widget
    with column_favorites:
        _draw_page_favorite(
            user=user,
        )

    # Draw "About me" widget
    with column_me:
        _draw_page_me(
            user=user,
        )
