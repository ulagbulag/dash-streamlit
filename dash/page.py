import streamlit as st

from dash.client import DashClient
from dash.modules.field import ValueField


# Create engines
client = DashClient()


def draw_page(*, namespace: str, function_name: str):
    # Get function
    function = client.get_function(
        namespace=namespace,
        name=function_name,
    )

    # Page information
    st.title(function.title())

    # Update inputs
    for field in function.data['spec']['input']:
        field = ValueField(namespace, field)
        field.update()

    commands = [
        'create',
        'delete',
        'exists',
    ]
    for (command_name, tab) in zip(
        commands,
        st.tabs([command.title() for command in commands]),
    ):
        if tab.button('Submit', key=command_name):
            tab.write(command_name)
