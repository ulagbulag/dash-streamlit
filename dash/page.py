import streamlit as st

from dash.client import DashClient
from dash.data.dynamic import DynamicObject
from dash.data.function import DashFunction
from dash.data.job import DashJob
from dash.modules import selector
from dash.modules.converter import to_dataframe
from dash.modules.field import ValueField


# Create engines
client = DashClient()


def draw_page(*, namespace: str, function_name: str) -> None:
    # Get function
    function = client.get_function(
        namespace=namespace,
        name=function_name,
    )

    # Page information
    st.title(function.title())

    # Show available commands
    commands = {
        'job list': _draw_page_job_list,
        'run': _draw_page_run,
    }
    for (tab, draw) in zip(
        st.tabs([command.title() for command in commands]),
        commands.values(),
    ):
        with tab:
            draw(
                function=function,
            )


def _draw_page_job_list(
    *, function: DashFunction,
) -> None:
    # Get metadata
    namespace = function.namespace()
    function_name = function.name()

    # Load jobs
    jobs = client.get_job_list_with_function_name(
        namespace=namespace,
        function_name=function_name,
    )

    # Convert to DataFrame
    df = to_dataframe(
        items=[
            j.data for j in jobs
        ],
        map=[
            ('name', '/metadata/name/'),
            ('state', '/status/state/'),
            ('created at', '/metadata/creationTimestamp/'),
            ('updated at', '/status/last_updated/'),
        ],
    )

    # Show DataFrame and Select Data
    jobs_selected = [
        next(
            job
            for job in jobs
            if job.name() == data['Name']
        )
        for data in selector.dataframe(df) or []
    ]

    # Compose available actions
    actions = {}
    # if len(jobs_selected) == 1:
    #     actions['show logs'] = _draw_page_job_show_logs
    if len(jobs_selected) >= 1:
        actions['delete'] = _draw_page_job_delete
        actions['restart'] = _draw_page_job_restart

    # Show actions
    st.markdown('## :zap: Actions')
    if actions:
        for (tab, draw) in zip(
            st.tabs([action.title() for action in actions]),
            actions.values(),
        ):
            with tab:
                draw(
                    function=function,
                    jobs=jobs_selected,
                )


def _draw_page_job_delete(
    *, function: DashFunction,
    jobs: list[DashJob],
) -> None:
    # Get metadata
    function_name = function.name()

    # Notify the caution
    _draw_caution_side_effect()

    # Apply
    if st.button('Delete', key=f'{function_name}_delete'):
        for job in jobs:
            client.delete_job(
                namespace=job.namespace(),
                function_name=function_name,
                job_name=job.name(),
            )
            with st.spinner(
                'Deleting ('
                f'{job.namespace()}::{job.name()}'
                ')...'
            ):
                st.success(
                    'Deleted ('
                    f'{job.namespace()}::{job.name()}'
                    ')',
                )

            # Remove data
            job.data = {}


def _draw_page_job_restart(
    *, function: DashFunction,
    jobs: list[DashJob],
) -> None:
    # Get metadata
    function_name = function.name()

    # Notify the caution
    _draw_caution_side_effect()

    # Apply
    if st.button('Restart', key=f'{function_name}_restart'):
        for job in jobs:
            new_job = client.restart_job(
                namespace=job.namespace(),
                function_name=function_name,
                job_name=job.name(),
            )
            with st.spinner(
                'Restarting ('
                f'{job.namespace()}::{job.name()}'
                ')...'
            ):
                st.success(
                    'Restarted ('
                    f'{job.namespace()}::{job.name()}'
                    ' => '
                    f'{new_job.namespace()}::{new_job.name()}'
                    ')',
                )

            # Replace data
            job.data = new_job.data


def _draw_page_run(
    *, function: DashFunction,
) -> None:
    # Get metadata
    namespace = function.namespace()
    function_name = function.name()

    # Update inputs
    value = DynamicObject(function.data['spec']['input'])
    for field in value.fields():
        field = ValueField(namespace, field)
        value.set(field.title(), field.update())

    # Apply
    if st.button('Create', key=f'{function_name}_run'):
        with st.spinner('Creating...'):
            new_job = client.post_job(
                namespace=namespace,
                function_name=function_name,
                value=value.data,
            )
        st.success(
            'Created ('
            f'{new_job.namespace()}::{new_job.name()}'
            ')',
        )


def _draw_caution_side_effect() -> None:
    st.warning('''
### :warning: Caution

This operation is **irreversible**.
Running operations will be terminated.
Unexpected shutdown may cause side effects!
''')
