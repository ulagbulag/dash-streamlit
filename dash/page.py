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


def draw_page(
    *, namespace: str | None, function: DashFunction,
) -> None:
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
                namespace=namespace,
                function=function,
            )


def _draw_page_job_list(
    *, namespace: str | None, function: DashFunction,
) -> None:
    # Get metadata
    function_name = function.name()

    # Load jobs
    jobs = client.get_job_list_with_function_name(
        namespace=namespace,
        function_name=function_name,
    )

    # Convert to DataFrame
    if jobs:
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
                        namespace=namespace,
                        function=function,
                        jobs=jobs_selected,
                    )
    else:
        st.info('Empty')


def _draw_page_job_delete(
    *, namespace: str | None, function: DashFunction,
    jobs: list[DashJob],
) -> None:
    # Get metadata
    user_name = client.user_name()
    function_name = function.name()

    # Notify the caution
    _draw_caution_side_effect()

    # Apply
    if st.button(
        label='Delete',
        key=f'/{user_name}/{namespace}/{function_name}/delete',
    ):
        for job in jobs:
            client.delete_job(
                namespace=namespace,
                function_name=function_name,
                job_name=job.name(),
            )
            with st.spinner(f'Deleting ({job.name()})...'):
                st.success(f'Requested Deleting ({job.name()})')
        _draw_reload_is_required()


def _draw_page_job_restart(
    *, namespace: str | None, function: DashFunction,
    jobs: list[DashJob],
) -> None:
    # Get metadata
    user_name = client.user_name()
    function_name = function.name()

    # Notify the caution
    _draw_caution_side_effect()

    # Apply
    if st.button(
        label='Restart',
        key=f'/{user_name}/{namespace}/{function_name}/restart',
    ):
        for job in jobs:
            new_job = client.restart_job(
                namespace=namespace,
                function_name=function_name,
                job_name=job.name(),
            )
            with st.spinner(f'Restarting ({job.name()})...'):
                st.success(
                    f'Requested Restarting ({job.name()} => {new_job.name()})',
                )
        _draw_reload_is_required()


def _draw_page_run(
    *, namespace: str | None, function: DashFunction,
) -> None:
    # Get metadata
    user_name = client.user_name()
    function_name = function.name()

    # Update inputs
    value = DynamicObject(function.data['spec']['input'])
    for field in value.fields():
        field = ValueField(namespace, field)
        value.set(field.title(), field.update())

    # Apply
    if st.button(
        label='Create',
        key=f'/{user_name}/{namespace}/{function_name}/create',
    ):
        with st.spinner('Creating...'):
            new_job = client.post_job(
                namespace=namespace,
                function_name=function_name,
                value=value.data,
            )
        st.success(f'Created ({new_job.name()})')
        _draw_reload_is_required()


def _draw_caution_side_effect() -> None:
    st.warning('''
### :warning: Caution

This operation is **irreversible**.
Running operations will be terminated.
Unexpected shutdown may cause side effects!
''')


def _draw_reload_is_required() -> None:
    st.info(':information_source: Press `R` or `rerun` button to reload jobs!')
