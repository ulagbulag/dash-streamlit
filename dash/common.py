import streamlit as st


def draw_caution_side_effect(
    message: str,
) -> None:
    if message:
        message = f'{message}\n'

    st.warning(f'''
### :warning: Caution

This operation is **irreversible**.{message}''')


def draw_caution_side_effect_database() -> None:
    return draw_caution_side_effect(
        message='''
Be sure to spell the **key** correctly, and remind yourself whether this is the **intended behavior**.
''',
    )


def draw_caution_side_effect_operation() -> None:
    return draw_caution_side_effect(
        message='''
Running operations will be terminated.
Unexpected shutdown may cause side effects!
''',
    )


def draw_reload_is_required() -> None:
    st.info(':information_source: Press `R` or `rerun` button to reload jobs!')
