import sys

import pytest

from onecode import OutputElement
from tests.utils.format import strip


def test_instantiation_error():
    with pytest.raises(TypeError) as excinfo:
        OutputElement(
            key='test',
            value='test_value',
        )

    py_version = sys.version_info
    err_str = "Can't instantiate abstract class OutputElement with abstract methods _validate"
    if sys.version_info >= (3, 12):
        err_str = strip("""
            Can't instantiate abstract class OutputElement without an implementation
            for abstract method '_validate'
        """)
    elif py_version >= (3, 9):
        err_str = "Can't instantiate abstract class OutputElement with abstract method _validate"

    assert err_str == str(excinfo.value)
