import os
import shutil

import pandas as pd
import pytest

from onecode import Mode, Project, JSONReader
from tests.utils.flow_cli import (
    _clean_flow,
    _generate_json_file,
    _generate_flow_name
)


def test_console_json_reader():
    Project().mode = Mode.CONSOLE

    widget = JSONReader(
        key="JSONReader",
        value=None,
        optional=True,
        testdata="data"
    )

    assert type(widget()) == JSONReader
    assert widget.testdata == "data"
    assert widget.kind == "JSONReader"
    assert widget.hide_when_disabled is False


def test_execute_single_json_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    json_file = _generate_json_file(folder_path, 'test.json')

    Project().mode = Mode.EXECUTE

    widget = JSONReader(
        key="JSONReader",
        value=json_file
    )

    pd.testing.assert_frame_equal(widget(), pd.read_json(json_file))
    assert widget.key == "JSONReader"
    assert widget.label == "JSONReader"
    assert widget._label == "JSONReader"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_multiple_json_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    json_file_1 = _generate_json_file(folder_path, 'test1.json')
    json_file_2 = _generate_json_file(folder_path, 'test2.json')

    Project().mode = Mode.EXECUTE

    widget = JSONReader(
        key="JSONReader",
        value=[json_file_1, json_file_2],
        count=2
    )

    value = widget()
    pd.testing.assert_frame_equal(value[0], pd.read_json(json_file_1))
    pd.testing.assert_frame_equal(value[1], pd.read_json(json_file_2))

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_optional_json_reader():
    Project().mode = Mode.EXECUTE

    widget = JSONReader(
        key="JSONReader",
        value=None,
        optional=True
    )

    assert widget() is None


def test_execute_invalid_path_json_reader():
    Project().mode = Mode.EXECUTE

    widget = JSONReader(
        key="JSONReader",
        value="nofile.json"
    )

    assert widget.value is None

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[JSONReader] Value is required: None provided" == str(excinfo.value)


def test_execute_invalid_single_json_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    json_file = _generate_json_file(folder_path, 'test.json')

    Project().mode = Mode.EXECUTE

    widget = JSONReader(
        key="JSONReader",
        value=json_file,
        count=1
    )
    with pytest.raises(TypeError) as excinfo:
        widget()

    assert """Invalid value    A  B  C
0  0  1  2
1  3  4  5, expected: list(<class 'pandas.core.frame.DataFrame'>)""" == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_multiple_json_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    json_file_1 = _generate_json_file(folder_path, 'test1.json')
    json_file_2 = _generate_json_file(folder_path, 'test2.json')

    Project().mode = Mode.EXECUTE

    widget = JSONReader(
        key="JSONReader",
        value=[json_file_1, json_file_2],
        count=None
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    assert """Invalid value type for [   A  B  C
0  0  1  2
1  3  4  5,    A  B  C
0  0  1  2
1  3  4  5], expected: <class 'pandas.core.frame.DataFrame'>""" == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_optional_json_reader():
    Project().mode = Mode.EXECUTE

    widget = JSONReader(
        key="JSONReader",
        value=None,
        optional=False
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[JSONReader] Value is required: None provided" == str(excinfo.value)


def test_build_gui_json_reader():
    Project().mode = Mode.BUILD_GUI

    widget = JSONReader(
        key="JSONReader",
        value=["/path/to/file.json"],
        label="My JSONReader",
        optional="$x$",
        count=2,
        tags=["json"]
    )

    assert widget() == ('JSONReader', {
        "key": "JSONReader",
        "kind": "JSONReader",
        "value": ["/path/to/file.json"],
        "label": "My JSONReader",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "tags": ["json"],
        "json_options": {
            "read_options": {},
            "convert_options": {},
        },
        'metadata': True,
        'depends_on': ['x']
    })


def test_extract_all_json_reader():
    Project().mode = Mode.EXTRACT_ALL

    widget = JSONReader(
        key="JSONReader",
        value=["/path/to/file.json"],
        label="My JSONReader",
        optional="$x$",
        count=2,
        tags=["json"]
    )

    assert widget() == ('JSONReader', {
        "key": "JSONReader",
        "kind": "JSONReader",
        "value": ["/path/to/file.json"],
        "label": "My JSONReader",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "tags": ["json"],
        "json_options": {
            "read_options": {},
            "convert_options": {}
        }
    })


def test_extract_all_json_reader_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "JSONReader": "/other_file.json"
    }

    widget = JSONReader(
        key="JSONReader",
        value=["/path/to/file.json"],
        label="My JSONReader",
        optional="$x$",
        count=2,
        tags=["json"]
    )

    assert widget() == ('JSONReader', {
        "key": "JSONReader",
        "kind": "JSONReader",
        "value": "/other_file.json",
        "label": "My JSONReader",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "tags": ["json"],
        "json_options": {
            "read_options": {},
            "convert_options": {}
        }
    })


def test_load_then_execute_json_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    json_file = _generate_json_file(folder_path, 'test.json')

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "JSONReader": json_file
    }

    widget = JSONReader(
        key="JSONReader",
        value=None,
        optional=True
    )

    pd.testing.assert_frame_equal(widget(), pd.read_json(json_file))
    assert widget.key == "JSONReader"
    assert widget.label == "JSONReader"
    assert widget._label == "JSONReader"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_json_reader_no_key():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    json_file = _generate_json_file(folder_path, 'test.json')

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_JSONReader": json_file
    }

    widget = JSONReader(
        key="JSONReader",
        value=None,
        optional=True
    )

    assert widget() is None
    assert widget.key == "JSONReader"
    assert widget.label == "JSONReader"
    assert widget._label == "JSONReader"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_empty_json_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    json_file = _generate_json_file(folder_path, 'test.json', empty=True)

    Project().mode = Mode.EXECUTE

    widget = JSONReader(
        key="JSONReader",
        value=json_file
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[JSONReader] Empty dataframe" == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_json_reader_metadata():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    json_file = _generate_json_file(folder_path, 'test.json')
    metadata = JSONReader.metadata(json_file)

    assert list(metadata.keys()) == ["columns", "stats"]
    assert metadata["columns"] == ["A", "B", "C"]
    assert isinstance(metadata["stats"], dict)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_json_reader_dependencies():
    widget = JSONReader(
        key="JSONReader",
        value=None,
        optional=True
    )

    assert widget.dependencies() == []

    widget = JSONReader(
        key="JSONReader",
        value=None,
        optional="len($df1$) > 1",
    )

    assert set(widget.dependencies()) == {"df1"}

    widget = JSONReader(
        key="JSONReader",
        value=None,
        optional=True,
        count="len($df1$)"
    )

    assert set(widget.dependencies()) == {"df1"}
