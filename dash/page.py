from datetime import datetime
import streamlit as st
from typing import Optional, Union

from dash import common
from dash.client import DashClient
from dash.data.dynamic import DynamicObject
from dash.data.function import DashFunction
from dash.data.job import DashJob
from dash.data.user import User
from dash.modules import selector
from dash.modules.converter import to_dataframe
from dash.modules.field import ValueField
from dash.storage.local import LocalStorage


# Create engines
client = DashClient()
storage = LocalStorage()


def draw_page(
    *, namespace: str | None, function: DashFunction,
    user: User,
) -> None:
    # Page information
    st.title(function.title())

    # Get metadata
    function_name = function.name()
    user_name = user.get_user_name()

    # Show available commands
    commands = {
        'job list': _draw_page_job_list,
        'run': _draw_page_run,
        'batch': _draw_page_batch,
    }
    for (tab, draw) in zip(
        st.tabs([command.title() for command in commands]),
        commands.values(),
    ):
        with tab:
            draw(
                namespace=namespace,
                function=function,
                storage_namespace=storage.get_namespace(
                    user_name=user_name,
                    kind='functions',
                    namespace=namespace,
                    name=function_name,
                ),
            )


def _draw_page_job_list(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
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
                ('updated at', '/status/lastUpdated/'),
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
        st.subheader(':zap: Actions')
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
    user_session = client.user_session()
    function_name = function.name()

    # Notify the caution
    common.draw_caution_side_effect_operation()

    # Apply
    if st.button(
        label='Delete',
        key=f'/{user_session}/function/{namespace}/{function_name}/delete',
    ):
        with st.spinner(f'Deleting...'):
            for job in jobs:
                client.delete_job(
                    namespace=namespace,
                    function_name=function_name,
                    job_name=job.name(),
                )
                with st.spinner(f'Deleting ({job.name()})...'):
                    st.success(f'Requested Deleting ({job.name()})')
        common.draw_reload_is_required()


def _draw_page_job_restart(
    *, namespace: str | None, function: DashFunction,
    jobs: list[DashJob],
) -> None:
    # Get metadata
    user_session = client.user_session()
    function_name = function.name()

    # Notify the caution
    common.draw_caution_side_effect_operation()

    # Apply
    if st.button(
        label='Restart',
        key=f'/{user_session}/function/{namespace}/{function_name}/restart',
    ):
        with st.spinner(f'Restarting...'):
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
        common.draw_reload_is_required()


def _draw_page_run(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
) -> None:
    # Update inputs
    value = DynamicObject(function.data['spec']['input'])
    for field in value.fields():
        field = ValueField(namespace, field)
        value.set(field.title(), field.update())

    # Show actions
    return _draw_page_action(
        namespace=namespace,
        function=function,
        storage_namespace=storage_namespace,
        prefix='run',
        values=value,
    )


def _draw_page_batch(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
) -> None:
    # Compose available uploading methods
    st.subheader(':anchor: Data Source')
    methods = [
        ('Database', _draw_page_batch_upload_database),
        ('Upload `.csv`', _draw_page_batch_upload_as_csv),
    ]

    # Upload inputs as csv
    for (_, method), tab in zip(methods, st.tabs([name for (name, _) in methods])):
        with tab:
            method(
                namespace=namespace,
                function=function,
                storage_namespace=storage_namespace,
            )


def _draw_page_batch_upload_as_csv(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
) -> None:
    # Get metadata
    user_session = client.user_session()
    function_name = function.name()

    # Update inputs
    uploaded_file = st.file_uploader(
        label='Please upload a batch `.csv` file. A .csv template cat be found on `Run` tab.',
        key=f'/{user_session}/function/{namespace}/{function_name}/batch/csv/upload',
        accept_multiple_files=False,
        type=['csv'],
    )
    if uploaded_file is None:
        return

    # Parse inputs
    template = DynamicObject(function.data['spec']['input'])
    values = template.from_csv(uploaded_file.getvalue())

    # Show inputs
    st.write(DynamicObject.collect_to_dataframe(values))

    # Show actions
    if len(values):
        return _draw_page_action(
            namespace=namespace,
            function=function,
            storage_namespace=storage_namespace,
            prefix='batch/csv',
            values=values,
        )


def _draw_page_batch_upload_database(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
) -> None:
    # Get metadata
    user_session = client.user_session()
    function_name = function.name()

    # Get user-saved keys
    with storage.namespaced(storage_namespace) as s:
        keys = s.list()
    if not keys:
        st.info('Empty')
        return

    # Select key
    key = st.selectbox(
        label='Select one of the templates below.',
        key=f'/{user_session}/function/{namespace}/{function_name}/batch/database/upload',
        options=keys,
    )
    if not key:
        return

    # Update inputs
    with storage.namespaced(storage_namespace) as s:
        data = s.get(key)
    if data is None:
        raise FileNotFoundError(f'No such key: {key}')

    # Parse inputs
    template = DynamicObject(function.data['spec']['input'])
    values = template.from_csv(data)

    # Show inputs
    st.write(DynamicObject.collect_to_dataframe(values))

    # Show actions
    if key and len(values):
        return _draw_page_action(
            namespace=namespace,
            function=function,
            storage_namespace=storage_namespace,
            prefix='batch/database',
            key=key,
            values=values,
        )


def _draw_page_action(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
    prefix: str,
    values: Union[DynamicObject, list[DynamicObject]],
    key: Optional[str] = None,
) -> None:
    # Compose available actions
    st.subheader(':zap: Actions')
    actions = [
        ('Create', _draw_page_action_create),
        ('Download as `.csv`', _draw_page_action_download_as_csv),
        ('Save to Database', _draw_page_action_download_database),
    ]
    if key:
        actions.append(
            ('Delete from Database', _draw_page_action_delete_database),
        )

    # Show actions
    for (_, action), column in zip(actions, st.tabs([name for name, _ in actions])):
        with column:
            action(
                namespace=namespace,
                function=function,
                storage_namespace=storage_namespace,
                prefix=prefix,
                key=key,
                values=values,
            )


def _draw_page_action_create(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
    prefix: str,
    key: Optional[str],
    values: Union[DynamicObject, list[DynamicObject]],
) -> None:
    # Get metadata
    user_session = client.user_session()
    function_name = function.name()

    # Apply
    if st.button(
        label='Click here to Submit',
        key=f'/{user_session}/function/{namespace}/{function_name}/{prefix}/create',
    ):
        if isinstance(values, DynamicObject):
            value = values
            with st.spinner('Creating...'):
                new_job = client.post_job(
                    namespace=namespace,
                    function_name=function_name,
                    value=value.data,
                )
            st.success(f'Created ({new_job.name()})')
        else:
            with st.spinner('Batch Creating...'):
                new_jobs = client.post_job_batch(
                    payload=[
                        {
                            'namespace': namespace,
                            'functionName': function_name,
                            'value': value.data,
                        }
                        for value in values
                    ],
                )
                new_jobs_names = ', '.join(
                    job.name()
                    for job in new_jobs
                )
                st.success(f'Created ({new_jobs_names})')
        common.draw_reload_is_required()


def _draw_page_action_download_as_csv(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
    prefix: str,
    key: Optional[str],
    values: Union[DynamicObject, list[DynamicObject]],
) -> None:
    # Get metadata
    user_session = client.user_session()
    function_name = function.name()

    # Collect data
    if isinstance(values, DynamicObject):
        value = values
        data = value.to_csv()
    else:
        data = DynamicObject.collect_to_csv(values)

    # Get filename
    file_name = f'[{datetime.now().isoformat()}] {namespace}_{function.title_raw()}.csv'
    st.caption(f'* File Name: {file_name}')

    # Apply
    file_name = f'[{datetime.now().isoformat()}] {namespace}_{function.title_raw()}.csv'
    st.download_button(
        label='Download',
        key=f'/{user_session}/function/{namespace}/{function_name}/{prefix}/download/csv',
        data=data,
        file_name=file_name,
    )


def _draw_page_action_download_database(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
    prefix: str,
    key: Optional[str],
    values: Union[DynamicObject, list[DynamicObject]],
) -> None:
    # Get metadata
    user_session = client.user_session()
    function_name = function.name()

    # Notify the caution
    common.draw_caution_side_effect_database()

    # Collect data
    if isinstance(values, DynamicObject):
        value = values
        data = value.to_csv()
    else:
        data = DynamicObject.collect_to_csv(values)

    # Apply
    key = st.text_input(
        label='Save to Database',
        key=f'/{user_session}/function/{namespace}/{function_name}/{prefix}/download/database/key',
        value=key or '',
    )
    if st.button(
        label='Save',
        key=f'/{user_session}/function/{namespace}/{function_name}/{prefix}/download/database/submit',
        disabled=not key,
    ) and key:
        with st.spinner('Saving...'):
            with storage.namespaced(storage_namespace) as s:
                s.set(key, data)
        st.success(':floppy_disk: Saved!')
        common.draw_reload_is_required()


def _draw_page_action_delete_database(
    *, namespace: str | None, function: DashFunction,
    storage_namespace: str,
    prefix: str,
    key: str,
    values: Union[DynamicObject, list[DynamicObject]],
) -> None:
    # Get metadata
    user_session = client.user_session()
    function_name = function.name()

    # Notify the caution
    common.draw_caution_side_effect_database()

    # Apply
    st.text_input(
        label='Delete from Database',
        key=f'/{user_session}/function/{namespace}/{function_name}/{prefix}/delete/database/key',
        value=key,
        disabled=True,
    )
    if st.button(
        label='Delete',
        key=f'/{user_session}/function/{namespace}/{function_name}/{prefix}/delete/database',
    ):
        with storage.namespaced(storage_namespace) as s:
            s.set(key, None)
        st.success(f':x: Deleted ({key})')
        common.draw_reload_is_required()
