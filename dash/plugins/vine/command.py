from pandas import DataFrame
import streamlit as st
from typing import Any, Hashable, Optional

from dash import common
from dash.client import DashClient
from dash.data.user import User
from dash.modules import selector
from dash.modules.converter import to_dataframe
from dash.storage.local import LocalStorage


# Create engines
client = DashClient()
storage = LocalStorage()


def draw_page(
    *, namespace: str, feature_name: str,
    user: User,
) -> None:
    # Page information
    st.title('Command')

    # Get metadata
    user_name = user.get_user_name()

    # Show available sessions
    sessions = DataFrame(
        session.to_dict()
        for session in client.get_user_session_list()
    )
    sessions_selected = selector.dataframe(
        df=sessions,
        show_selected=False,
    )
    if not sessions_selected:
        return

    # Get target nodes
    # st.subheader(':desktop_computer: Select')
    # nodes = client.get_model_item_list(
    #     namespace=namespace,
    #     name='box',
    # )
    # nodes_selected = selector.dataframe(
    #     df=to_dataframe(
    #         items=[
    #             node.data for node in nodes
    #         ],
    #         map=[
    #             ('id', '/metadata/name', False),
    #             ('name', '/metadata/labels/dash.ulagbulag.io~1alias', True),
    #             ('state', '/status/state/', False),
    #         ],
    #     ),
    #     show_selected=False,
    # )
    # if not nodes_selected:
    #     return

    # Show available commands
    st.subheader(':zap: Action')
    commands = {
        'Database': _draw_page_database,
        'Execute': _draw_page_execute,
    }
    for (tab, draw) in zip(
        st.tabs([command.title() for command in commands]),
        commands.values(),
    ):
        with tab:
            draw(
                namespace=namespace,
                feature_name=feature_name,
                user_name=user_name,
                storage_namespace=f'/{user_name}/{namespace}/plugins/{feature_name}',
                sessions=sessions_selected,
            )


def _draw_page_database(
    *, namespace: str, feature_name: str,
    user_name: str, storage_namespace: str,
    sessions: list[dict[Hashable, Any]],
) -> None:
    # Get metadata
    user_session = client.user_session()

    # Get user-saved keys
    with storage.namespaced(storage_namespace) as s:
        keys = s.list()
    if not keys:
        st.info('Empty')
        return

    # Select key
    key = st.selectbox(
        label='Select one of the templates below.',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/batch/database/upload',
        options=keys,
    )
    if not key:
        return

    # Update inputs
    with storage.namespaced(storage_namespace) as s:
        data = s.get(key)
    if data is None:
        raise FileNotFoundError(f'No such key: {key}')

    # Parse inputs
    command = data.decode('utf-8')

    # Show command
    command = st.text_input(
        label='Please enter the command to execute for all PCs.',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/batch/database/command',
        value=command,
    )

    # Show options
    option_terminal = st.checkbox(
        label='Open with a new Terminal (GUI Command)',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/batch/database/option/terminal',
    )

    # Show actions
    if key and command:
        return _draw_page_action(
            namespace=namespace,
            feature_name=feature_name,
            user_name=user_name,
            storage_namespace=storage_namespace,
            prefix='batch/database',
            key=key,
            command=command,
            sessions=sessions,
            option_terminal=option_terminal,
        )


def _draw_page_execute(
    *, namespace: str, feature_name: str,
    user_name: str, storage_namespace: str,
    sessions: list[dict[Hashable, Any]],
) -> None:
    # Get metadata
    user_session = client.user_session()

    # Get command
    command = st.text_input(
        label='Please enter the command to execute for all PCs.',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/batch/raw/command',
    )

    # Show options
    option_terminal = st.checkbox(
        label='Open with a new Terminal (GUI Command)',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/batch/raw/option/terminal',
    )

    # Show actions
    if command:
        return _draw_page_action(
            namespace=namespace,
            feature_name=feature_name,
            user_name=user_name,
            storage_namespace=storage_namespace,
            prefix='batch/raw',
            command=command,
            sessions=sessions,
            option_terminal=option_terminal,
        )


def _draw_page_action(
    *, namespace: str, feature_name: str,
    user_name: str, storage_namespace: str,
    prefix: str,
    key: Optional[str] = None,
    command: str,
    sessions: list[dict[Hashable, Any]],
    option_terminal: bool,
) -> None:
    # Compose available actions
    st.subheader(':zap: Actions')
    actions = [
        ('Run', _draw_page_action_run),
        ('Save to Database', _draw_page_action_download_database),
    ]
    if key:
        actions.append(
            ('Delete from Database', _draw_page_action_delete_database),
        )

    # Show actions
    for (_, action), column in zip(actions, st.tabs([name for name, _ in actions])):
        with column:
            action(
                namespace=namespace,
                feature_name=feature_name,
                user_name=user_name,
                storage_namespace=storage_namespace,
                prefix=prefix,
                key=key,
                command=command,
                sessions=sessions,
                option_terminal=option_terminal,
            )


def _draw_page_action_run(
    *, namespace: str, feature_name: str,
    user_name: str, storage_namespace: str,
    prefix: str,
    key: Optional[str],
    command: str,
    sessions: list[dict[Hashable, Any]],
    option_terminal: bool,
) -> None:
    # Get metadata
    user_session = client.user_session()

    # Apply
    if st.button(
        label='Run',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/{prefix}/run',
    ):
        with st.spinner('Batch Running...'):
            client.post_user_exec_broadcast(
                command=command,
                option_terminal=option_terminal,
                target_user_names=[
                    session['Name']
                    for session in sessions
                ],
            )
            st.success('Finished')


def _draw_page_action_download_database(
    *, namespace: str, feature_name: str,
    user_name: str, storage_namespace: str,
    prefix: str,
    key: Optional[str] = None,
    command: str,
    sessions: list[dict[Hashable, Any]],
    option_terminal: bool,
) -> None:
    # Get metadata
    user_session = client.user_session()

    # Notify the caution
    common.draw_caution_side_effect_database()

    # Apply
    key = st.text_input(
        label='Save to Database',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/{prefix}/download/database/key',
        value=key or '',
    )
    if st.button(
        label='Save',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/{prefix}/download/database/submit',
        disabled=not key,
    ) and key:
        with st.spinner('Saving...'):
            with storage.namespaced(storage_namespace) as s:
                s.set(key, command)
        st.success(':floppy_disk: Saved!')
        common.draw_reload_is_required()


def _draw_page_action_delete_database(
    *, namespace: str, feature_name: str,
    user_name: str, storage_namespace: str,
    prefix: str,
    key: str,
    command: str,
    sessions: list[dict[Hashable, Any]],
    option_terminal: bool,
) -> None:
    # Get metadata
    user_session = client.user_session()

    # Notify the caution
    common.draw_caution_side_effect_database()

    # Apply
    st.text_input(
        label='Delete from Database',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/{prefix}/delete/database/key',
        value=key,
        disabled=True,
    )
    if st.button(
        label='Delete',
        key=f'/{user_session}/plugin/{namespace}/{feature_name}/{prefix}/delete/database',
    ):
        with storage.namespaced(storage_namespace) as s:
            s.set(key, None)
        st.success(f':x: Deleted ({key})')
        common.draw_reload_is_required()
