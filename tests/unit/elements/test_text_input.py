import pytest

from onecode import Mode, Project, TextInput
from tests.utils.format import strip


def test_console_single_text_input():
    Project().mode = Mode.CONSOLE

    widget = TextInput(
        key="TextInput",
        value="My Text",
        testdata="data"
    )

    assert type(widget()) == TextInput
    assert widget.testdata == "data"
    assert widget.kind == "TextInput"


def test_execute_single_text_input():
    Project().mode = Mode.EXECUTE

    widget = TextInput(
        key="TextInput",
        value="My Text"
    )

    assert widget() == "My Text"
    assert widget.key == "textinput"
    assert widget.label == "TextInput"
    assert widget._label == "TextInput"


def test_execute_multiple_text_input():
    Project().mode = Mode.EXECUTE

    widget = TextInput(
        key="TextInput",
        value=["My Text 1", "My Text 2", "My Text 3"],
        count=3
    )

    assert widget() == ["My Text 1", "My Text 2", "My Text 3"]


def test_execute_optional_text_input():
    Project().mode = Mode.EXECUTE

    widget = TextInput(
        key="TextInput",
        value=None,
        optional=True
    )

    assert widget() is None


def test_execute_invalid_single_text_input():
    Project().mode = Mode.EXECUTE

    widget = TextInput(
        key="TextInput",
        value="My Text",
        count=1
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value My Text, expected: list(<class 'str'>)" == str(excinfo.value)


def test_execute_invalid_multiple_text_input():
    Project().mode = Mode.EXECUTE

    widget = TextInput(
        key="TextInput",
        value=["My Text 1", "My Text 2", "My Text 3"],
        count=None
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert strip("""
        Invalid value type for ['My Text 1', 'My Text 2', 'My Text 3'],
        expected: <class 'str'>
    """) == str(excinfo.value)


def test_execute_invalid_optional_text_input():
    Project().mode = Mode.EXECUTE

    widget = TextInput(
        key="TextInput",
        value=None,
        optional=False
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[textinput] Value is required: None provided" == str(excinfo.value)


def test_extract_all_text_input():
    Project().mode = Mode.EXTRACT_ALL

    widget = TextInput(
        key="TextInput",
        value=["OneCode", "rocks!"],
        label="My TextInput",
        optional="$x$",
        count=2,
        max_chars=500,
        placeholder="My Placeholder"
    )

    assert widget() == ('textinput', {
        "key": "textinput",
        "kind": "TextInput",
        "value": ["OneCode", "rocks!"],
        "label": "My TextInput",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "max_chars": 500,
        "placeholder": "My Placeholder",
        "multiline": False
    })


def test_extract_all_text_input_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "textinput": "OneCode rocks!"
    }

    widget = TextInput(
        key="TextInput",
        value=["OneCode", "rocks!"],
        label="My TextInput",
        optional="$x$",
        count=2,
        max_chars=500,
        placeholder="My Placeholder",
        multiline=True
    )

    assert widget() == ('textinput', {
        "key": "textinput",
        "kind": "TextInput",
        "value": "OneCode rocks!",
        "label": "My TextInput",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "max_chars": 500,
        "placeholder": "My Placeholder",
        "multiline": True
    })


def test_load_then_execute_text_input():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "textinput": "OneCode rocks!"
    }

    widget = TextInput(
        key="TextInput",
        value=None,
        optional=True
    )

    assert widget() == "OneCode rocks!"
    assert widget.key == "textinput"
    assert widget.label == "TextInput"
    assert widget._label == "TextInput"


def test_load_then_execute_text_input_no_key():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_textinput": "OneCode rocks!"
    }

    widget = TextInput(
        key="TextInput",
        value=None,
        optional=True
    )

    assert widget() is None
    assert widget.key == "textinput"
    assert widget.label == "TextInput"
    assert widget._label == "TextInput"
