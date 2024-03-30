import sys

import pytest

from onecode import InputElement
from tests.utils.format import strip


def test_instantiation_error():
    with pytest.raises(TypeError) as excinfo:
        InputElement(
            key='test',
            value='test_value',
        )

    err_str = strip("""
        Can't instantiate abstract class InputElement with abstract methods
        _validate, _value_type
    """)

    if sys.version_info >= (3, 12):
        err_str = strip("""
            Can't instantiate abstract class InputElement without an implementation
            for abstract methods _validate', '_value_type'
        """)

    assert err_str == str(excinfo.value)
