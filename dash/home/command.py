import os
import streamlit as st


from dash.client import DashClient
from dash.data.command import Command
from dash.data.resource import ResourceRef
from dash.data.user import User
from dash.search import SearchEngine
from dash.storage.local import LocalStorage


# Create engines
client = DashClient()
try:
    search_engine = SearchEngine()
except ImportError as e:
    search_engine = None
    print(e)
storage = LocalStorage()


def draw_page(
    *, functions: dict[str, list[ResourceRef]],
    user: User,
) -> None:
    # Test
    if not search_engine:
        return

    # Get metadata
    user_name = user.name
    user_session = client.user_session()

    # SKip if not admin
    if not user.role_admin:
        return

    # Store all commands
    commands: list[Command] = []
    for namespace, functions_namespaced in functions.items():
        for function in functions_namespaced:
            # command = Command(
            #     kind='functions',
            #     name=function.name,
            #     namespace=function.namespace,
            #     key=None,
            # )
            # commands.append(command)
            # search_engine.add_function(
            #     function=command.search_engine_function_name,
            #     action=command.action,
            #     witnesses=[],
            # )
            with storage.namespaced(storage.get_namespace(
                user_name=user_name,
                kind='functions',
                namespace=namespace,
                name=function.name,
            )) as s:
                for key in s.list():
                    command = Command(
                        kind='functions',
                        name=function.name,
                        namespace=function.namespace,
                        key=key,
                    )
                    commands.append(command)
                    search_engine.add_function(
                        function=command.search_engine_function_name,
                        action=command.action,
                        witnesses=[],
                    )

    # Get user query
    query = st.text_input(
        label=':heavy_dollar_sign: Command here',
        key=f'/{user_session}/home/command/query',
    )

    # Search actions
    if query:
        actions = search_engine.search(
            query=query,
        )
        if not actions:
            st.info('Empty')
            return

        # Select an action
        action = actions[0]

        # Parse the action
        command_ref = Command.from_str(action)
    else:
        command_ref = None

    # Parse command
    command_selected = st.selectbox(
        label=':zap: Action',
        key=f'/{user_session}/home/command/query/command',
        options=commands,
        index=commands.index(command_ref) if command_ref is not None else 0,
    )
    if not command_selected:
        return

    # Update command
    is_need_training = command_ref != command_selected

    # Action
