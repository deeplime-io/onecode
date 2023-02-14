from typing import Any

import pytest

from onecode import InputElement, Keyword, Mode, Project


@pytest.fixture
def my_input_element():
    class _MyInputElement(InputElement):
        def __init__(
            self,
            key: str,
            value: str,
            optional: bool,
            count: int,
            hide_when_disabled
        ):
            super().__init__(
                key,
                value,
                optional=optional,
                count=count,
                hide_when_disabled=hide_when_disabled
            )

        @property
        def _value_type(self) -> type:
            return str

        def streamlit(
            self,
            id: str
        ) -> str:
            return f"""# Just Write BEGIN
st.write('{self.value}', key={id})
# Just Write END"""

        def _validate(
            self,
            value: Any
        ) -> None:
            pass

    return _MyInputElement


def test_streamlit_input_element_required_no_count_shown(my_input_element):
    Project().mode = Mode.STREAMLIT

    widget = my_input_element(
        'Just Write',
        'hello',
        optional=False,
        count=None,
        hide_when_disabled=False
    )

    assert widget() == f"""# Just Write BEGIN
st.write('hello', key='just_write')
# Just Write END
{Keyword.DATA}['just_write'] = just_write if not (False) else None

"""


def test_streamlit_input_element_optional_bool_no_count_shown(my_input_element):
    Project().mode = Mode.STREAMLIT

    widget = my_input_element(
        'Just Write',
        'hello',
        optional=True,
        count=None,
        hide_when_disabled=False
    )

    assert widget() == f"""
_optional_just_write = not st.checkbox(
    'Enable ' + '''Just Write''',
    value=True,
    key='_optional_just_write'
)
# Just Write BEGIN
st.write('hello', key='just_write')
# Just Write END
{Keyword.DATA}['just_write'] = just_write if not (_optional_just_write) else None

"""


def test_streamlit_input_element_optional_str_no_count_shown(my_input_element):
    Project().mode = Mode.STREAMLIT

    widget = my_input_element(
        'Just Write',
        'hello',
        optional='$x$',
        count=None,
        hide_when_disabled=False
    )

    assert widget() == f"""# Just Write BEGIN
st.write('hello', key='just_write')
# Just Write END
{Keyword.DATA}['just_write'] = just_write if not ({Keyword.DATA}["x"]) else None

"""


def test_streamlit_input_element_optional_bool_with_count_shown(my_input_element):
    Project().mode = Mode.STREAMLIT

    widget = my_input_element(
        'Just Write',
        'hello',
        optional=True,
        count=1,
        hide_when_disabled=False
    )

    assert widget() == f"""
_optional_just_write = not st.checkbox(
    'Enable ' + '''Just Write''',
    value=True,
    key='_optional_just_write'
)

{Keyword.DATA}['just_write'] = []
for _c in range(int(1)):
        # Just Write BEGIN
    st.write('hello', key=f'just_write_{{_c}}')
    # Just Write END
    {Keyword.DATA}['just_write'].append(just_write if not (_optional_just_write) else None)
"""


def test_streamlit_input_element_optional_bool_no_count_hidden(my_input_element):
    Project().mode = Mode.STREAMLIT

    widget = my_input_element(
        'Just Write',
        'hello',
        optional=True,
        count=None,
        hide_when_disabled=True
    )

    assert widget() == f"""
_optional_just_write = not st.checkbox(
    'Enable ' + '''Just Write''',
    value=True,
    key='_optional_just_write'
)
if not (_optional_just_write):    # Just Write BEGIN
    st.write('hello', key='just_write')
    # Just Write END
{Keyword.DATA}['just_write'] = just_write if not (_optional_just_write) else None

"""


def test_streamlit_input_element_optional_bool_with_count_hidden(my_input_element):
    Project().mode = Mode.STREAMLIT

    widget = my_input_element(
        'Just Write',
        'hello',
        optional=True,
        count=1,
        hide_when_disabled=True
    )

    assert widget() == f"""
_optional_just_write = not st.checkbox(
    'Enable ' + '''Just Write''',
    value=True,
    key='_optional_just_write'
)

{Keyword.DATA}['just_write'] = []
for _c in range(int(1)):
    if not (_optional_just_write):        # Just Write BEGIN
        st.write('hello', key=f'just_write_{{_c}}')
        # Just Write END
    {Keyword.DATA}['just_write'].append(just_write if not (_optional_just_write) else None)
"""
