import pytest

from onecode import Mode, Project, Slider


def test_console_single_slider():
    Project().mode = Mode.CONSOLE

    widget = Slider(
        key="Slider",
        value=0.6,
        step=0.1,
        testdata="data"
    )

    assert type(widget()) == Slider
    assert widget.testdata == "data"
    assert widget.kind == "Slider"
    assert widget.hide_when_disabled is False


def test_execute_single_slider():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=0.6,
        step=0.1
    )

    assert widget() == 0.6
    assert widget.key == "slider"
    assert widget.label == "Slider"
    assert widget._label == "Slider"


def test_execute_single_slider_int_value():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=2,
        step=1,
        min=0,
        max=5
    )

    assert widget() == 2
    assert isinstance(widget(), int)
    assert widget.key == "slider"
    assert widget.label == "Slider"
    assert widget._label == "Slider"


def test_execute_multiple_slider():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=[0.6, 0.3, 0.4],
        count=3,
        step=0.1
    )

    assert widget() == [0.6, 0.3, 0.4]


def test_execute_multiple_slider_int_values():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=[2, 1, 3],
        count=3,
        step=1,
        min=0,
        max=5
    )

    assert widget() == [2, 1, 3]
    assert all(isinstance(v, int) for v in widget())


def test_execute_optional_slider():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=None,
        optional=True
    )

    assert widget() is None


def test_execute_invalid_single_slider():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=0.6,
        count=1,
        step=0.1
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value 0.6, expected: list(typing.Union[float, int])" == str(excinfo.value)


def test_execute_invalid_multiple_slider():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=[0.6, 0.3, 0.4],
        count=None,
        step=0.1
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value type for [0.6, 0.3, 0.4], expected: typing.Union[float, int]" == \
        str(excinfo.value)


def test_execute_invalid_min_max_single_slider():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=5.1,
        min=5.2,
        max=6,
        step=0.1
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[slider] Value lower than minimum: 5.1 < 5.2" == str(excinfo.value)

    Project().reset()
    Project().mode = Mode.EXECUTE
    widget = Slider(
        key="Slider",
        value=5.3,
        min=5,
        max=5.2,
        step=0.1
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[slider] Value greater than maximum: 5.3 > 5.2" == str(excinfo.value)

    Project().reset()
    Project().mode = Mode.EXECUTE
    widget = Slider(
        key="Slider",
        value=5.25,
        max=5.2,
        min=5.3,
        step=0.01
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[slider] Minimum cannot be greater than maximum: 5.3 > 5.2" == str(excinfo.value)


def test_execute_invalid_min_max_multiple_slider():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=[5.3, 5.1],
        min=5.2,
        max=6,
        count=2,
        step=0.1
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[slider] Value lower than minimum: 5.1 < 5.2" == str(excinfo.value)

    Project().reset()
    Project().mode = Mode.EXECUTE
    widget = Slider(
        key="Slider",
        value=[5.1, 5.3],
        min=5,
        max=5.2,
        count=2,
        step=0.1
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[slider] Value greater than maximum: 5.3 > 5.2" == str(excinfo.value)

    Project().reset()
    Project().mode = Mode.EXECUTE
    widget = Slider(
        key="Slider",
        value=[5.25, 5.25],
        max=5.2,
        min=5.3,
        count=2,
        step=0.01
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[slider] Minimum cannot be greater than maximum: 5.3 > 5.2" == str(excinfo.value)


def test_execute_invalid_optional_slider():
    Project().mode = Mode.EXECUTE

    widget = Slider(
        key="Slider",
        value=None,
        optional=False
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[slider] Value is required: None provided" == str(excinfo.value)


def test_build_gui_slider():
    Project().mode = Mode.BUILD_GUI

    widget = Slider(
        key="Slider",
        value=[0.5, 12.3],
        label="My Slider",
        optional="$x$",
        count=2,
        min=0.1,
        max=15.6,
        step=0.1
    )

    assert widget() == ('slider', {
        "key": "slider",
        "kind": "Slider",
        "value": [0.5, 12.3],
        "min": 0.1,
        "max": 15.6,
        "step": 0.1,
        "label": "My Slider",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        'metadata': False,
        'depends_on': ['x']
    })


def test_extract_all_slider():
    Project().mode = Mode.EXTRACT_ALL

    widget = Slider(
        key="Slider",
        value=[0.5, 12.3],
        label="My Slider",
        optional="$x$",
        count=2,
        min=0.1,
        max=15.6,
        step=0.1
    )

    assert widget() == ('slider', {
        "key": "slider",
        "kind": "Slider",
        "value": [0.5, 12.3],
        "min": 0.1,
        "max": 15.6,
        "step": 0.1,
        "label": "My Slider",
        "disabled": '$x$',
        "optional": True,
        "count": 2
    })


def test_extract_all_slider_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "slider": [0.1, 0.6]
    }

    widget = Slider(
        key="Slider",
        value=[0.5, 12.3],
        label="My Slider",
        optional="$x$",
        count=2,
        min=0.1,
        max=15.6,
        step=0.1
    )

    assert widget() == ('slider', {
        "key": "slider",
        "kind": "Slider",
        "value": [0.1, 0.6],
        "min": 0.1,
        "max": 15.6,
        "step": 0.1,
        "label": "My Slider",
        "disabled": '$x$',
        "optional": True,
        "count": 2
    })


def test_load_then_execute_slider():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "slider": [0.1, 0.6]
    }

    widget = Slider(
        key="Slider",
        value=None,
        optional=True,
        count=2
    )

    assert widget() == [0.1, 0.6]
    assert widget.key == "slider"
    assert widget.label == "Slider"
    assert widget._label == "Slider"


def test_load_then_execute_slider_no_key():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_slider": [0.1, 0.6]
    }

    widget = Slider(
        key="Slider",
        value=None,
        optional=True,
        count=2
    )

    assert widget() is None
    assert widget.key == "slider"
    assert widget.label == "Slider"
    assert widget._label == "Slider"


def test_slider_metadata():
    metadata = Slider.metadata(True)

    assert metadata == {}


def test_slider_dependencies():
    widget = Slider(
        key="Slider",
        value=None,
        optional=True
    )

    assert widget.dependencies() == []

    widget = Slider(
        key="Slider",
        value=None,
        optional="len($df1$) > 1",
    )

    assert set(widget.dependencies()) == {"df1"}

    widget = Slider(
        key="Slider",
        value=None,
        optional=True,
        count="len($df1$)"
    )

    assert set(widget.dependencies()) == {"df1"}
