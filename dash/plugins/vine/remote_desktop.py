import streamlit as st
import streamlit.components.v1 as components

from dash.client import DashClient
from dash.data.session import SessionRef


# Create engines
client = DashClient()


def draw_page(
    *, namespace: str, feature_name: str,
    user_name: str,
) -> None:
    # Page information
    st.title('Remote Desktop')

    # Get metadata
    user_session = client.user_session()

    # Show available sessions
    sessions = client.get_user_session_list()
    session = st.selectbox(
        label='Select one of the sessions below.',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/query/session',
        options=sessions,
    )
    if not session:
        return

    # Show available commands
    commands = {
        'Show': _draw_page_show,
        'Open with a new Tab': _draw_page_open,
    }
    for (tab, draw) in zip(
        st.tabs([command.title() for command in commands]),
        commands.values(),
    ):
        with tab:
            draw(
                session=session,
            )


def _draw_page_show(
    *, session: SessionRef,
) -> None:
    # Action
    components.iframe(
        src=session.novnc_lite_url,
        height=830,
    )


def _draw_page_open(
    *, session: SessionRef,
) -> None:
    # Action
    st.markdown(
        body=f'<a href="{session.novnc_full_url}" style="display: inline-block; padding: 12px 20px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; font-size: 16px; border-radius: 4px;">Open link in a new Tab</a>',
        unsafe_allow_html=True,
    )
