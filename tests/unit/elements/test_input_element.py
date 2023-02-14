import pytest

from onecode import InputElement
from tests.utils.format import strip


def test_instantiation_error():
    with pytest.raises(TypeError) as excinfo:
        InputElement(
            key='test',
            value='test_value',
        )

    assert strip("""
        Can't instantiate abstract class InputElement with abstract methods
        _validate, _value_type, streamlit
    """) == \
        str(excinfo.value)
