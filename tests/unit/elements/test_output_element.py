import pytest

from onecode import OutputElement
from tests.utils.format import strip


def test_instantiation_error():
    with pytest.raises(TypeError) as excinfo:
        OutputElement(
            key='test',
            value='test_value',
        )

    assert strip("""
        Can't instantiate abstract class OutputElement with abstract method
        _validate
    """) == \
        str(excinfo.value)
