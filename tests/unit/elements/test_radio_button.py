import pytest

from onecode import Mode, Project, RadioButton


def test_console_single_radio_button():
    Project().mode = Mode.CONSOLE

    widget = RadioButton(
        key="RadioButton",
        value="A",
        options=["A", "B"],
        metadata="data"
    )

    assert type(widget()) == RadioButton
    assert widget.metadata == "data"
    assert widget.kind == "RadioButton"


def test_execute_single_radio_button():
    Project().mode = Mode.EXECUTE

    widget = RadioButton(
        key="RadioButton",
        value="A",
        options=["A", "B"]
    )

    assert widget() == "A"
    assert widget.key == "radiobutton"
    assert widget.label == "RadioButton"
    assert widget._label == "RadioButton"


def test_execute_multiple_radio_button():
    Project().mode = Mode.EXECUTE

    widget = RadioButton(
        key="RadioButton",
        value=["A", "B"],
        options=["A", "B"],
        count=2
    )

    assert widget() == ["A", "B"]


def text_execute_optional_radio_button():
    Project().mode = Mode.EXECUTE

    widget = RadioButton(
        key="RadioButton",
        value=None,
        options=["A", "B"],
        optional=True
    )

    assert widget() is None


def test_execute_invalid_single_radio_button():
    Project().mode = Mode.EXECUTE

    widget = RadioButton(
        key="RadioButton",
        value="A",
        options=["A", "B"],
        count=1
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value A, expected: list(<class 'str'>)" == str(excinfo.value)


def text_execute_invalid_optional_radio_button():
    Project().mode = Mode.EXECUTE

    widget = RadioButton(
        key="RadioButton",
        value=None,
        options=["A", "B"],
        optional=False
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[radiobutton] Value is required: None provided" == str(excinfo.value)


def test_execute_invalid_option():
    Project().mode = Mode.EXECUTE

    widget = RadioButton(
        key="RadioButton",
        value="C",
        options=["A", "B"],
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[radiobutton] Not a valid choice: C" == str(excinfo.value)


def test_extract_all_radio_button():
    Project().mode = Mode.EXTRACT_ALL

    widget = RadioButton(
        key="RadioButton",
        value=["A", "C"],
        label="My RadioButton",
        optional="$x$",
        count=2,
        options=["A", "B", "C"],
        horizontal=True
    )

    assert widget() == ('radiobutton', {
        "key": "radiobutton",
        "kind": "RadioButton",
        "value": ["A", "C"],
        "label": "My RadioButton",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "options": ["A", "B", "C"],
        "horizontal": True
    })


def test_extract_all_radio_button_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "radiobutton": "B"
    }

    widget = RadioButton(
        key="RadioButton",
        value=["A", "C"],
        label="My RadioButton",
        optional="$x$",
        count=2,
        options=["A", "B", "C"],
        horizontal=True
    )

    assert widget() == ('radiobutton', {
        "key": "radiobutton",
        "kind": "RadioButton",
        "value": "B",
        "label": "My RadioButton",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "options": ["A", "B", "C"],
        "horizontal": True
    })


def test_load_then_execute_radio_button():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "radiobutton": "B"
    }

    widget = RadioButton(
        key="RadioButton",
        value=None,
        optional=True,
        options=["A", "B", "C"]
    )

    assert widget() == "B"
    assert widget.key == "radiobutton"
    assert widget.label == "RadioButton"
    assert widget._label == "RadioButton"


def test_load_then_execute_radio_button_no_key():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_radiobutton": "B"
    }

    widget = RadioButton(
        key="RadioButton",
        value=None,
        optional=True,
        options=["A", "B", "C"]
    )

    assert widget() is None
    assert widget.key == "radiobutton"
    assert widget.label == "RadioButton"
    assert widget._label == "RadioButton"
