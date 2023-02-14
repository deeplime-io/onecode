from typing import Any

import pytest

from onecode import Mode, OutputElement, Project


@pytest.fixture
def my_output_element():
    class _MyOutputElement(OutputElement):
        def __init__(
            self,
            key: str,
            value: str,
            label: str,
            extra: int
        ):
            super().__init__(key, value, label, extra=extra)

        @staticmethod
        def streamlit() -> str:
            return """# Just Write BEGIN
st.write(f'{key} - {label}: {value}')
# Just Write END"""

        def _validate(
            self,
            value: Any
        ) -> None:
            pass

    return _MyOutputElement


def test_streamlit_output_element(my_output_element):
    Project().mode = Mode.STREAMLIT

    widget = my_output_element(
        'Just Write',
        'hello',
        label='Hello write',
        extra=5
    )

    assert widget() == """
def __MyOutputElement(key=None, label=None, value=None, kind=None, extra=None):
    # Just Write BEGIN
    st.write(f'{key} - {label}: {value}')
    # Just Write END
"""
