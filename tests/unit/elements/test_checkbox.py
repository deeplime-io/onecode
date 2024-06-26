import pytest

from onecode import Checkbox, Mode, Project


def test_console_checkbox():
    Project().mode = Mode.CONSOLE

    widget = Checkbox(
        key="Checkbox",
        value=True,
        testdata="data"
    )

    assert type(widget()) == Checkbox
    assert widget.testdata == "data"
    assert widget.kind == "Checkbox"
    assert widget.hide_when_disabled is False


def test_execute_single_checkbox():
    Project().mode = Mode.EXECUTE

    widget = Checkbox(
        key="Checkbox",
        value=True
    )

    assert widget() is True
    assert widget.key == "checkbox"
    assert widget.label == "Checkbox"
    assert widget._label == "Checkbox"


def test_execute_multiple_checkbox():
    Project().mode = Mode.EXECUTE

    widget = Checkbox(
        key="Checkbox",
        value=[True, False, True],
        count=3
    )

    assert widget() == [True, False, True]


def test_execute_optional_checkbox():
    Project().mode = Mode.EXECUTE

    widget = Checkbox(
        key="Checkbox",
        value=None,
        optional=True
    )

    assert widget() is None


def test_execute_invalid_single_checkbox():
    Project().mode = Mode.EXECUTE

    widget = Checkbox(
        key="Checkbox",
        value=True,
        count=1
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value True, expected: list(<class 'bool'>)" == str(excinfo.value)


def test_execute_invalid_multiple_checkbox():
    Project().mode = Mode.EXECUTE

    widget = Checkbox(
        key="Checkbox",
        value=[True, False, True],
        count=None
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value type for [True, False, True], expected: <class 'bool'>" == \
        str(excinfo.value)


def test_execute_invalid_optional_checkbox():
    Project().mode = Mode.EXECUTE

    widget = Checkbox(
        key="Checkbox",
        value=None,
        optional=False
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[checkbox] Value is required: None provided" == str(excinfo.value)


def test_build_gui_checkbox():
    Project().mode = Mode.BUILD_GUI

    widget = Checkbox(
        key="Checkbox",
        value=[True, True],
        label="My Checkbox",
        optional="$x$",
        count=2
    )

    assert widget() == ('checkbox', {
        "key": "checkbox",
        "kind": "Checkbox",
        "value": [True, True],
        "label": "My Checkbox",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        'metadata': False,
        'depends_on': ['x']
    })


def test_extract_all_checkbox():
    Project().mode = Mode.EXTRACT_ALL

    widget = Checkbox(
        key="Checkbox",
        value=[True, True],
        label="My Checkbox",
        optional="$x$",
        count=2
    )

    assert widget() == ('checkbox', {
        "key": "checkbox",
        "kind": "Checkbox",
        "value": [True, True],
        "label": "My Checkbox",
        "disabled": '$x$',
        "optional": True,
        "count": 2
    })


def test_extract_all_checkbox_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "checkbox": False
    }

    widget = Checkbox(
        key="Checkbox",
        value=[True, True],
        label="My Checkbox",
        optional="$x$",
        count=2
    )

    assert widget() == ('checkbox', {
        "key": "checkbox",
        "kind": "Checkbox",
        "value": False,
        "label": "My Checkbox",
        "disabled": '$x$',
        "optional": True,
        "count": 2
    })


def test_load_then_execute_checkbox():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "checkbox": False
    }

    widget = Checkbox(
        key="Checkbox",
        value=None,
        optional=True
    )

    assert widget() is False
    assert widget.key == "checkbox"
    assert widget.label == "Checkbox"
    assert widget._label == "Checkbox"


def test_load_then_execute_checkbox_no_key():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_checkbox": False
    }

    widget = Checkbox(
        key="Checkbox",
        value=None,
        optional=True
    )

    assert widget() is None
    assert widget.key == "checkbox"
    assert widget.label == "Checkbox"
    assert widget._label == "Checkbox"


def test_checkbox_metadata():
    metadata = Checkbox.metadata(True)

    assert metadata == {}


def test_checkbox_dependencies():
    widget = Checkbox(
        key="Checkbox",
        value=None,
        optional=True
    )

    assert widget.dependencies() == []

    widget = Checkbox(
        key="Checkbox",
        value=None,
        optional="len($df1$) > 1",
    )

    assert set(widget.dependencies()) == {"df1"}

    widget = Checkbox(
        key="Checkbox",
        value=None,
        optional=True,
        count="len($df1$)"
    )

    assert set(widget.dependencies()) == {"df1"}
