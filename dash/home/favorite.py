import streamlit as st

from dash.client import DashClient
from dash.common import draw_reload_is_required
from dash.data.user import User


# Create engines
client = DashClient()


def draw_page(*, user: User) -> None:
    # Get metadata
    user_name = user.get_user_name()
    user_session = client.user_session()

    # Page Information
    st.subheader(':star: Favorites')

    # # Monitor data changing
    # is_me_changed = False

    # user_name_input = st.text_input(
    #     label='Name',
    #     key=f'/{user_session}/home/favorite/name',
    #     value=user_name,
    # )
    # is_me_changed |= user_name == user_name_input

    # st.text_input(
    #     label='Desktop Image',
    #     key=f'/{user_session}/home/favorite/desktop/image',
    # )

    # # Apply
    # if st.button(
    #     label='Apply',
    #     key=f'/{user_session}/home/favorite',
    #     disabled=is_me_changed,
    # ):
    #     st.success('Updated')
    #     return draw_reload_is_required()
