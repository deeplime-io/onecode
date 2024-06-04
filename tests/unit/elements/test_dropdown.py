import pytest

from onecode import Dropdown, Mode, Project


def test_console_single_dropdown():
    Project().mode = Mode.CONSOLE

    widget = Dropdown(
        key="Dropdown",
        value="A",
        options=["A", "B"],
        testdata="data"
    )

    assert type(widget()) == Dropdown
    assert widget.testdata == "data"
    assert widget.kind == "Dropdown"
    assert widget.hide_when_disabled is False


def test_execute_single_dropdown_single_choice():
    Project().mode = Mode.EXECUTE

    widget = Dropdown(
        key="Dropdown",
        value="A",
        options=["A", "B"]
    )

    assert widget() == "A"
    assert widget.key == "dropdown"
    assert widget.label == "Dropdown"
    assert widget._label == "Dropdown"


def test_execute_single_dropdown_multiple_choice():
    Project().mode = Mode.EXECUTE

    widget = Dropdown(
        key="Dropdown",
        value=["A", "C"],
        options=["A", "B", "C"],
        multiple=True
    )

    assert widget() == ["A", "C"]


def test_execute_multiple_dropdown_single_choice():
    Project().mode = Mode.EXECUTE

    widget = Dropdown(
        key="Dropdown",
        value=["A", "B"],
        options=["A", "B"],
        count=2
    )

    assert widget() == ["A", "B"]


def test_execute_multiple_dropdown_multiple_choice():
    Project().mode = Mode.EXECUTE

    widget = Dropdown(
        key="Dropdown",
        value=[["A", "C"], ["B"]],
        options=["A", "B", "C"],
        multiple=True,
        count=2
    )

    assert widget() == [["A", "C"], ["B"]]


def text_execute_optional_dropdown():
    Project().mode = Mode.EXECUTE

    widget = Dropdown(
        key="Dropdown",
        value=None,
        options=["A", "B"],
        optional=True
    )

    assert widget() is None


def test_execute_invalid_single_dropdown_single_choice():
    Project().mode = Mode.EXECUTE

    widget = Dropdown(
        key="Dropdown",
        value="A",
        options=["A", "B"],
        count=1
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value A, expected: list(typing.Union[str, int, float])" == str(excinfo.value)


def test_execute_invalid_single_dropdown_multiple_choice():
    Project().mode = Mode.EXECUTE

    widget = Dropdown(
        key="Dropdown",
        value=["A", "C"],
        options=["A", "B", "C"],
        multiple=True,
        count=1
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value type for each element of ['A', 'C'], expected: " \
           "typing.List[typing.Union[str, int, float]]" == str(excinfo.value)


def text_execute_invalid_optional_dropdown():
    Project().mode = Mode.EXECUTE

    widget = Dropdown(
        key="Dropdown",
        value=None,
        options=["A", "B"],
        optional=False
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[dropdown] Value is required: None provided" == str(excinfo.value)


def test_execute_invalid_option():
    Project().mode = Mode.EXECUTE

    widget = Dropdown(
        key="Dropdown",
        value="C",
        options=["A", "B"],
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[dropdown] Not a valid choice: C" == str(excinfo.value)


def test_build_gui_dropdown():
    Project().mode = Mode.BUILD_GUI

    widget = Dropdown(
        key="Dropdown",
        value=[["A", "B"], ["C"]],
        label="My Dropdown",
        optional="$x$",
        count=2,
        multiple=True,
        options=["A", "B", "C"]
    )

    assert widget() == ('dropdown', {
        "key": "dropdown",
        "kind": "Dropdown",
        "value": [["A", "B"], ["C"]],
        "label": "My Dropdown",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "multiple": True,
        "options": ["A", "B", "C"],
        'metadata': False,
        'depends_on': ['x']
    })


def test_extract_all_dropdown():
    Project().mode = Mode.EXTRACT_ALL

    widget = Dropdown(
        key="Dropdown",
        value=[["A", "B"], ["C"]],
        label="My Dropdown",
        optional="$x$",
        count=2,
        multiple=True,
        options=["A", "B", "C"]
    )

    assert widget() == ('dropdown', {
        "key": "dropdown",
        "kind": "Dropdown",
        "value": [["A", "B"], ["C"]],
        "label": "My Dropdown",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "multiple": True,
        "options": ["A", "B", "C"]
    })


def test_extract_all_dropdown_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "dropdown": ["A", "B"]
    }

    widget = Dropdown(
        key="Dropdown",
        value=[["A", "B"], ["C"]],
        label="My Dropdown",
        optional="$x$",
        count=2,
        multiple=True,
        options=["A", "B", "C"]
    )

    assert widget() == ('dropdown', {
        "key": "dropdown",
        "kind": "Dropdown",
        "value": ["A", "B"],
        "label": "My Dropdown",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "multiple": True,
        "options": ["A", "B", "C"]
    })


def test_load_then_execute_dropdown():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "dropdown": ["A", "B"]
    }

    widget = Dropdown(
        key="Dropdown",
        value=None,
        optional=True,
        options=["A", "B", "C"],
        multiple=True
    )

    assert widget() == ["A", "B"]
    assert widget.key == "dropdown"
    assert widget.label == "Dropdown"
    assert widget._label == "Dropdown"


def test_load_then_execute_dropdown_no_key():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_dropdown": ["A", "B"]
    }

    widget = Dropdown(
        key="Dropdown",
        value=None,
        optional=True,
        options=["A", "B", "C"],
        multiple=True
    )

    assert widget() is None
    assert widget.key == "dropdown"
    assert widget.label == "Dropdown"
    assert widget._label == "Dropdown"


def test_dropdown_metadata():
    metadata = Dropdown.metadata(True)

    assert metadata == {}


def test_dropdown_dependencies():
    widget = Dropdown(
        key="Dropdown",
        value=None,
        optional=True,
        options=["A", "B", "C"],
        multiple=True
    )

    assert widget.dependencies() == []

    widget = Dropdown(
        key="Dropdown",
        value=None,
        optional="len($df1$) > 1",
        options="$df2$.columns",
        multiple=True
    )

    assert set(widget.dependencies()) == {"df1", "df2"}

    widget = Dropdown(
        key="Dropdown",
        value=None,
        optional=True,
        options="$df2$.columns",
        count="len($df1$)",
        multiple=True
    )

    assert set(widget.dependencies()) == {"df1", "df2"}
