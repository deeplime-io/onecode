import pytest

from onecode import Mode, NumberInput, Project


def test_console_single_number_input():
    Project().mode = Mode.CONSOLE

    widget = NumberInput(
        key="NumberInput",
        value=5.1,
        min=5,
        max=6
    )

    assert type(widget()) == NumberInput


def test_execute_single_number_input():
    Project().mode = Mode.EXECUTE

    widget = NumberInput(
        key="NumberInput",
        value=5.1,
        min=5,
        max=6
    )

    assert widget() == 5.1
    assert widget.key == "numberinput"
    assert widget.label == "'''NumberInput'''"
    assert widget._label == "NumberInput"


def test_execute_multiple_number_input():
    Project().mode = Mode.EXECUTE

    widget = NumberInput(
        key="NumberInput",
        value=[5.1, 2.3, 4.6],
        count=3
    )

    assert widget() == [5.1, 2.3, 4.6]


def test_execute_optional_number_input():
    Project().mode = Mode.EXECUTE

    widget = NumberInput(
        key="NumberInput",
        value=None,
        optional=True
    )

    assert widget() is None


def test_execute_invalid_single_number_input():
    Project().mode = Mode.EXECUTE

    widget = NumberInput(
        key="NumberInput",
        value=5.1,
        count=1
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value 5.1, expected: list(<class 'float'>)" == str(excinfo.value)


def test_execute_invalid_multiple_number_input():
    Project().mode = Mode.EXECUTE

    widget = NumberInput(
        key="NumberInput",
        value=[5.1, 2.3, 4.6],
        count=None
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert "Invalid value type for [5.1, 2.3, 4.6], expected: <class 'float'>" == \
        str(excinfo.value)


def test_execute_invalid_min_max_single_number_input():
    Project().mode = Mode.EXECUTE

    widget = NumberInput(
        key="NumberInput",
        value=5.1,
        min=5.2
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[numberinput] Value lower than minimum: 5.1 < 5.2" == str(excinfo.value)

    Project().reset()
    Project().mode = Mode.EXECUTE
    widget = NumberInput(
        key="NumberInput",
        value=5.3,
        max=5.2
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[numberinput] Value greater than maximum: 5.3 > 5.2" == str(excinfo.value)

    Project().reset()
    Project().mode = Mode.EXECUTE
    widget = NumberInput(
        key="NumberInput",
        value=5.25,
        max=5.2,
        min=5.3
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[numberinput] Minimum cannot be greater than maximum: 5.3 > 5.2" == str(excinfo.value)


def test_execute_invalid_min_max_multiple_number_input():
    Project().mode = Mode.EXECUTE

    widget = NumberInput(
        key="NumberInput",
        value=[5.3, 5.1],
        min=5.2,
        count=2
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[numberinput] Value lower than minimum: 5.1 < 5.2" == str(excinfo.value)

    Project().reset()
    Project().mode = Mode.EXECUTE
    widget = NumberInput(
        key="NumberInput",
        value=[5.1, 5.3],
        max=5.2,
        count=2
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[numberinput] Value greater than maximum: 5.3 > 5.2" == str(excinfo.value)

    Project().reset()
    Project().mode = Mode.EXECUTE
    widget = NumberInput(
        key="NumberInput",
        value=[5.25, 5.25],
        max=5.2,
        min=5.3,
        count=2
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[numberinput] Minimum cannot be greater than maximum: 5.3 > 5.2" == str(excinfo.value)


def test_execute_invalid_optional_number_input():
    Project().mode = Mode.EXECUTE

    widget = NumberInput(
        key="NumberInput",
        value=None,
        optional=False
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[numberinput] Value is required: None provided" == str(excinfo.value)


def test_extract_all_number_input():
    Project().mode = Mode.EXTRACT_ALL

    widget = NumberInput(
        key="NumberInput",
        value=[0.5, 12.3],
        label="My NumberInput",
        optional="$x$",
        count=2,
        min=0.1,
        max=15.6,
        step=0.1
    )

    assert widget() == ('numberinput', {
        "key": "numberinput",
        "kind": "NumberInput",
        "value": [0.5, 12.3],
        "min": 0.1,
        "max": 15.6,
        "step": 0.1,
        "label": "My NumberInput",
        "disabled": '_DATA_["x"]',
        "optional": True,
        "count": "2"
    })


def test_extract_all_number_input_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "numberinput": [0.12, 16.5]
    }

    widget = NumberInput(
        key="NumberInput",
        value=[0.5, 12.3],
        label="My NumberInput",
        optional="$x$",
        count=2,
        min=0.1,
        max=15.6,
        step=0.1
    )

    assert widget() == ('numberinput', {
        "key": "numberinput",
        "kind": "NumberInput",
        "value": [0.12, 16.5],
        "min": 0.1,
        "max": 15.6,
        "step": 0.1,
        "label": "My NumberInput",
        "disabled": '_DATA_["x"]',
        "optional": True,
        "count": "2"
    })


def test_load_then_execute_number_input():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "numberinput": [0.12, 16.5]
    }

    widget = NumberInput(
        key="NumberInput",
        value=None,
        optional=True,
        count=2
    )

    assert widget() == [0.12, 16.5]
    assert widget.key == "numberinput"
    assert widget.label == "'''NumberInput'''"
    assert widget._label == "NumberInput"


def test_load_then_execute_number_input_no_key():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_numberinput": [0.12, 16.5]
    }

    widget = NumberInput(
        key="NumberInput",
        value=None,
        optional=True,
        count=2
    )

    assert widget() is None
    assert widget.key == "numberinput"
    assert widget.label == "'''NumberInput'''"
    assert widget._label == "NumberInput"
