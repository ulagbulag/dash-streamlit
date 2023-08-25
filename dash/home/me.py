import streamlit as st

from dash.client import DashClient
from dash.common import draw_reload_is_required
from dash.data.user import User


# Create engines
client = DashClient()


def draw_page(*, user: User) -> None:
    # Get metadata
    user_session = client.user_session()

    # Page Information
    st.subheader(':raised_hands: About me')

    # Monitor data changing
    is_me_changed = False

    def user_input(
        is_me_changed: bool,
        key: str,
        label: str | None = None,
        disabled: bool = False,
    ) -> tuple[str, bool]:
        input_default: str = getattr(user, key)
        input_value = st.text_input(
            label=label or key.title(),
            key=f'/{user_session}/home/me/{key}',
            value=input_default,
            disabled=disabled,
        ) or ''
        is_me_changed |= input_default != input_value
        return (input_value, is_me_changed)

    user_name_input, is_me_changed = user_input(
        is_me_changed=is_me_changed,
        key='name',
        disabled=True,
    )
    user_nickname_input, is_me_changed = user_input(
        is_me_changed=is_me_changed,
        key='nickname',
        disabled=True,
    )
    user_email_input, is_me_changed = user_input(
        is_me_changed=is_me_changed,
        key='email',
        label='E-Mail',
        disabled=True,
    )
    user_tel_office_input, is_me_changed = user_input(
        is_me_changed=is_me_changed,
        key='tel_office',
        label='Tel. Office',
        disabled=True,
    )
    user_tel_phone_input, is_me_changed = user_input(
        is_me_changed=is_me_changed,
        key='tel_phone',
        label='Tel. Mobile',
        disabled=True,
    )
    user_image_input, is_me_changed = user_input(
        is_me_changed=is_me_changed,
        key='image',
        label='Desktop Image',
        disabled=True,
    )

    # Apply
    if st.button(
        label='Apply',
        key=f'/{user_session}/home/me',
        disabled=not is_me_changed,
    ):
        st.success('Updated')
        return draw_reload_is_required()
