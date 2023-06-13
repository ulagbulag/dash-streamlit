import streamlit as st
from streamlit.errors import StreamlitAPIException

from dash.client import DashClient
from dash.page import draw_page


@st.cache_resource()
def load_functions(namespace: str | None = None):
    # Load DASH Client
    client = DashClient()

    # Load functions
    functions = client.get_function_list(namespace=namespace)

    # Sort by namespace and name
    return {
        namespace: sorted(
            (
                function for function in functions
                if function.namespace == namespace
            ),
            key=lambda f: f.name,
        )
        for namespace in sorted(
            function.namespace for function in functions
        )
    }


def load_pages():
    # Load DASH Client
    client = DashClient()

    # Load Functions
    with st.spinner('Initializing...'):
        try:
            functions = load_functions(namespace='*')
        except Exception:
            functions = load_functions()

    # Load Cached Function
    function_selected = st.session_state.get('/', None)

    # Load Pages
    with st.sidebar:
        for namespace, functions_namespaced in functions.items():
            with st.expander(namespace, expanded=True):
                for function_ref in functions_namespaced:
                    function = client.get_function(
                        namespace=function_ref.namespace,
                        name=function_ref.name,
                    )
                    if st.button(
                        label=function.title(),
                        key=f'/{function.namespace()}/{function.name()}',
                        type='primary' if function == function_selected else 'secondary',
                        use_container_width=True,
                    ):
                        function_selected = st.session_state['/'] = function
                        st.experimental_rerun()

    # Load Selected Page
    if function_selected is not None:
        draw_page(
            function=function_selected,
        )
    else:
        # Page Information
        st.title('Welcome to OpenARK Dashboard')


if __name__ == '__main__':
    # Page Configuration
    try:
        st.set_page_config(layout='wide')
    except StreamlitAPIException:
        pass

    load_pages()
