import streamlit as st

from dash.client import DashClient
from dash.modules.field import ValueField


# Create engines
client = DashClient()


def draw_page(*, function_name: str):
    # Get function
    function = client.get_function(
        name=function_name,
    )

    # Page information
    st.title(function.title())

    # Update inputs
    for field in function.data['spec']['input']:
        field = ValueField(field)
        field.update()

    # st.write(function.data)
