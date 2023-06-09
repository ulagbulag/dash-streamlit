import os
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
import streamlit as st

from dash.client import DashClient


# @st.cache_resource()
def load_pages():
    # Load DASH Client
    client = DashClient()

    # Load functions
    functions = client.get_function_list(namespace='*')

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
    for index, function_ref in enumerate(functions, start=1):
        function = client.get_function(
            namespace=function_ref.namespace,
            name=function_ref.name,
        )
        with open(f'./pages/{index:04d}_{function.title().replace(" ", "_")}.py', 'w') as f:
            f.write(template.render(
                namespace=function_ref.namespace,
                function_name=function_ref.name,
            ))


# Page Information
st.title('Welcome to OpenARK Dashboard')

with st.spinner('Initializing...'):
    load_pages()
