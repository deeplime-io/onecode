import sys
from typing import Any

import pytest

from onecode import InputElement, Project
from tests.utils.format import strip


@pytest.fixture
def my_input_element():
    class _MyInputElement(InputElement):
        def __init__(
            self,
            key: str,
            value: str,
            label: str,
            extra: int
        ):
            super().__init__(key, value, label, extra=extra)

        @property
        def _value_type(self) -> type:
            return str

        def _validate(
            self,
            value: Any
        ) -> None:
            pass

    return _MyInputElement


def test_extend_input_element(my_input_element):
    x = my_input_element('test', 'test_value', None, 5)

    assert x.key == "test"
    assert x.label == "test"
    assert x._label == "test"
    assert x.value == 'test_value'
    assert x.extra == 5

    x = my_input_element('Test again', 'test_value', "my label", 5)

    assert x.key == "test_again"
    assert x.label == "my label"
    assert x._label == "my label"
    assert x.value == 'test_value'
    assert x.extra == 5


def test_extend_input_element_missing_validate():
    class _MyInputElement(InputElement):
        def __init__(
            self,
            key: str,
            value: str,
            label: str,
            extra: int
        ):
            super().__init__(key, value, label, extra=extra)

        @property
        def _value_type(self) -> type:
            return str

    with pytest.raises(TypeError) as excinfo:
        _MyInputElement('test', 'test_value', None, 5)

    py_version = sys.version_info
    err_str = "Can't instantiate abstract class _MyInputElement with abstract methods _validate"
    if sys.version_info >= (3, 12):
        err_str = strip("""
            Can't instantiate abstract class _MyInputElement without an implementation
            for abstract method '_validate'
        """)
    elif py_version >= (3, 9):
        err_str = "Can't instantiate abstract class _MyInputElement with abstract method _validate"

    assert err_str == str(excinfo.value)


def test_extend_input_element_invalid_extra_args():
    class _MyInputElement(InputElement):
        def __init__(
            self,
            key: str,
            value: str,
            label: str,
            extra: int
        ):
            super().__init__(
                key,
                value,
                label,
                disabled=extra,
                __eq__='equal',
                _value='new_value',
                kind="Kind"
            )

        @property
        def _value_type(self) -> type:
            return str

        def _validate(
            self,
            value: Any
        ) -> None:
            pass

    with pytest.raises(AttributeError) as excinfo:
        _MyInputElement('test', 'test_value', None, 5)

    assert strip("""The following parameters are reserved:
        ['disabled', '__eq__', '_value', 'kind']""") == str(excinfo.value)


def test_extend_invalid_key_input_element(my_input_element):
    with pytest.raises(ValueError) as excinfo:
        my_input_element(' ', 'test_value', None, 5)

    assert "Key cannot be null" == str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        my_input_element('_x', 'test_value', None, 5)

    assert 'Key starting with "_" are reserved: _x' == str(excinfo.value)


def test_extend_invalid_call_method(my_input_element):
    Project().mode = "Fake"
    x = my_input_element('test', 'test_value', None, 5)

    with pytest.raises(ValueError) as excinfo:
        x()

    assert "Unknown Project mode Fake" == str(excinfo.value)
