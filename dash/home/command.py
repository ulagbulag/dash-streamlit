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
search_engine = SearchEngine()
storage = LocalStorage()


def draw_page(
    *, functions: dict[str, list[ResourceRef]],
    user: User,
) -> None:
    # Get metadata
    user_name = user.get_user_name()
    user_session = client.user_session()

    # SKip if not admin
    if not user.get_role_admin():
        return

    # Store all commands
    commands = []
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
    if not query:
        return

    # Search actions
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

    # Parse command
    command = st.selectbox(
        label=':package: Command',
        key=f'/{user_session}/home/command/query/command',
        options=commands,
        index=commands.index(command_ref),
    )
