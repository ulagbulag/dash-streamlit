import os
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
import streamlit as st

from dash.client import DashClient


# @st.cache_resource()
def load_pages():
    # Load DASH Client
    client = DashClient()

    # Cleanup Pages
    shutil.rmtree('./pages', ignore_errors=True)
    os.mkdir('./pages')

    # Load Page Template
    env = Environment(
        loader=FileSystemLoader(
            searchpath='./templates/',
        ),
        autoescape=select_autoescape(),
    )
    template = env.get_template('function.py.j2')

    # Load Pages
    for index, function_name in enumerate(client.get_function_list(), start=1):
        function = client.get_function(name=function_name)
        with open(f'./pages/{index:04d}_{function.title().replace(" ", "_")}.py', 'w') as f:
            f.write(template.render(
                function_name=function_name,
            ))


# Page Information
st.title('Welcome to OpenARK Dashboard')

with st.spinner('Initializing...'):
    load_pages()
