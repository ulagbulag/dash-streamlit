import streamlit as st
from streamlit.errors import StreamlitAPIException
from types import ModuleType

from dash import plugins as _plugins
from dash.client import DashClient
from dash.page import draw_page


@st.cache_resource(ttl=300)  # 5 minutes
def load_functions(
    *,
    namespace: str | None = None,
    user_session: int,
):
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
    user_session = client.user_session()
    user_name = client.get_user_name()

    # Load Plugins
    plugins = {
        plugin.replace('_', '-'): {
            feature: (
                plugin,
                feature,
                getattr(getattr(getattr(_plugins, plugin), feature), 'draw_page'),
            )
            for feature in dir(getattr(_plugins, plugin))
            if not feature.startswith('_')
            and isinstance(getattr(getattr(_plugins, plugin), feature), ModuleType)
            and hasattr(getattr(getattr(_plugins, plugin), feature), 'draw_page')
        }
        for plugin in dir(_plugins)
        if not plugin.startswith('_')
        and isinstance(getattr(_plugins, plugin), ModuleType)
    }

    # Load Functions
    with st.spinner('Initializing...'):
        try:
            functions = load_functions(
                namespace='*',
                user_session=user_session,
            )
            is_admin = True
        except Exception:
            functions = load_functions(
                user_session=user_session,
            )
            is_admin = False

    # Load cache items
    function_selected = st.session_state.get(f'/{user_session}/function', None)
    plugin_selected = st.session_state.get(f'/{user_session}/plugin', None)

    # Load Pages
    with st.sidebar:
        if st.button(
            label=':house: Home',
            key=f'/{user_session}/home',
            type='primary'
                if function_selected is None and plugin_selected is None
                else 'secondary',
            use_container_width=True,
        ):
            function_selected = st.session_state[f'/{user_session}/function'] = None
            plugin_selected = st.session_state[f'/{user_session}/plugin'] = None
            st.experimental_rerun()

        # Merge namespaces
        namespaces = sorted(set(functions.keys()).union(plugins.keys()))

        for namespace in namespaces:
            with st.expander(namespace, expanded=True):
                # Plugin
                if namespace in plugins:
                    for feature_name in plugins[namespace]:
                        feature = plugins[namespace][feature_name]
                        if st.button(
                            label=feature_name.title().replace('_', ' '),
                            key=f'/{user_session}/plugin/{namespace}/{feature_name}',
                            type='primary' if feature[:2] == plugin_selected else 'secondary',
                            use_container_width=True,
                        ):
                            function_selected = st.session_state[f'/{user_session}/function'] = None
                            plugin_selected = st.session_state[f'/{user_session}/plugin'] = feature[:2]
                            st.experimental_rerun()

                # Dash Function
                for function_ref in functions.get(namespace, []):
                    function = client.get_function(
                        namespace=function_ref.namespace if is_admin else None,
                        name=function_ref.name,
                    )
                    if st.button(
                        label=function.title(),
                        key=f'/{user_session}/function/{function.namespace()}/{function.name()}',
                        type='primary' if function == function_selected else 'secondary',
                        use_container_width=True,
                    ):
                        function_selected = st.session_state[f'/{user_session}/function'] = function
                        plugin_selected = st.session_state[f'/{user_session}/plugin'] = None
                        st.experimental_rerun()

    # Load Selected Page
    if function_selected is not None:
        draw_page(
            namespace=function_selected.namespace() if is_admin else None,
            function=function_selected,
            user_name=user_name,
        )
    elif plugin_selected is not None:
        namespace, feature_name, _draw_page = \
            plugins[plugin_selected[0]][plugin_selected[1]]
        _draw_page(
            namespace=namespace,
            feature_name=feature_name,
            user_name=user_name,
        )
    else:
        _draw_home_page()


def _draw_home_page() -> None:
    # Page Information
    st.title('Welcome to OpenARK Dashboard')


if __name__ == '__main__':
    # Page Configuration
    try:
        st.set_page_config(layout='wide')
    except StreamlitAPIException:
        pass

    load_pages()
