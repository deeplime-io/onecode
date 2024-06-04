import os
import shutil

import pandas as pd
import pytest

from onecode import CsvReader, Mode, Project
from tests.utils.flow_cli import (
    _clean_flow,
    _generate_csv_file,
    _generate_flow_name
)


def test_console_csv_reader():
    Project().mode = Mode.CONSOLE

    widget = CsvReader(
        key="CsvReader",
        value=None,
        optional=True,
        testdata="data"
    )

    assert type(widget()) == CsvReader
    assert widget.testdata == "data"
    assert widget.kind == "CsvReader"
    assert widget.hide_when_disabled is False


def test_execute_single_csv_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.EXECUTE

    widget = CsvReader(
        key="CsvReader",
        value=csv_file
    )

    pd.testing.assert_frame_equal(widget(), pd.read_csv(csv_file))
    assert widget.key == "csvreader"
    assert widget.label == "CsvReader"
    assert widget._label == "CsvReader"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_multiple_csv_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file_1 = _generate_csv_file(folder_path, 'test1.csv')
    csv_file_2 = _generate_csv_file(folder_path, 'test2.csv')

    Project().mode = Mode.EXECUTE

    widget = CsvReader(
        key="CsvReader",
        value=[csv_file_1, csv_file_2],
        count=2
    )

    value = widget()
    pd.testing.assert_frame_equal(value[0], pd.read_csv(csv_file_1))
    pd.testing.assert_frame_equal(value[1], pd.read_csv(csv_file_2))

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_optional_csv_reader():
    Project().mode = Mode.EXECUTE

    widget = CsvReader(
        key="CsvReader",
        value=None,
        optional=True
    )

    assert widget() is None


def test_execute_invalid_path_csv_reader():
    Project().mode = Mode.EXECUTE

    widget = CsvReader(
        key="CsvReader",
        value="nofile.csv"
    )

    assert widget.value is None

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[csvreader] Value is required: None provided" == str(excinfo.value)


def test_execute_invalid_single_csv_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.EXECUTE

    widget = CsvReader(
        key="CsvReader",
        value=csv_file,
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


def test_execute_invalid_multiple_csv_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file_1 = _generate_csv_file(folder_path, 'test1.csv')
    csv_file_2 = _generate_csv_file(folder_path, 'test2.csv')

    Project().mode = Mode.EXECUTE

    widget = CsvReader(
        key="CsvReader",
        value=[csv_file_1, csv_file_2],
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


def test_execute_invalid_optional_csv_reader():
    Project().mode = Mode.EXECUTE

    widget = CsvReader(
        key="CsvReader",
        value=None,
        optional=False
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[csvreader] Value is required: None provided" == str(excinfo.value)


def test_build_gui_csv_reader():
    Project().mode = Mode.BUILD_GUI

    widget = CsvReader(
        key="CsvReader",
        value=["/path/to/file.csv"],
        label="My CsvReader",
        optional="$x$",
        count=2,
        tags=["CSV"]
    )

    assert widget() == ('csvreader', {
        "key": "csvreader",
        "kind": "CsvReader",
        "value": ["/path/to/file.csv"],
        "label": "My CsvReader",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "tags": ["CSV"],
        'metadata': True,
        'depends_on': ['x']
    })


def test_extract_all_csv_reader():
    Project().mode = Mode.EXTRACT_ALL

    widget = CsvReader(
        key="CsvReader",
        value=["/path/to/file.csv"],
        label="My CsvReader",
        optional="$x$",
        count=2,
        tags=["CSV"]
    )

    assert widget() == ('csvreader', {
        "key": "csvreader",
        "kind": "CsvReader",
        "value": ["/path/to/file.csv"],
        "label": "My CsvReader",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "tags": ["CSV"]
    })


def test_extract_all_csv_reader_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "csvreader": "/other_file.csv"
    }

    widget = CsvReader(
        key="CsvReader",
        value=["/path/to/file.csv"],
        label="My CsvReader",
        optional="$x$",
        count=2,
        tags=["CSV"]
    )

    assert widget() == ('csvreader', {
        "key": "csvreader",
        "kind": "CsvReader",
        "value": "/other_file.csv",
        "label": "My CsvReader",
        "disabled": '$x$',
        "optional": True,
        "count": 2,
        "tags": ["CSV"]
    })


def test_load_then_execute_csv_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "csvreader": csv_file
    }

    widget = CsvReader(
        key="CsvReader",
        value=None,
        optional=True
    )

    pd.testing.assert_frame_equal(widget(), pd.read_csv(csv_file))
    assert widget.key == "csvreader"
    assert widget.label == "CsvReader"
    assert widget._label == "CsvReader"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_csv_reader_no_key():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_csvreader": csv_file
    }

    widget = CsvReader(
        key="CsvReader",
        value=None,
        optional=True
    )

    assert widget() is None
    assert widget.key == "csvreader"
    assert widget.label == "CsvReader"
    assert widget._label == "CsvReader"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_empty_csv_reader():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv', empty=True)

    Project().mode = Mode.EXECUTE

    widget = CsvReader(
        key="CsvReader",
        value=csv_file
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[csvreader] Empty dataframe" == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_csv_reader_metadata():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')
    metadata = CsvReader.metadata(csv_file)

    assert list(metadata.keys()) == ["columns", "stats"]
    assert metadata["columns"] == ["A", "B", "C"]
    assert isinstance(metadata["stats"], dict)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_csv_reader_dependencies():
    widget = CsvReader(
        key="CsvReader",
        value=None,
        optional=True
    )

    assert widget.dependencies() == []

    widget = CsvReader(
        key="CsvReader",
        value=None,
        optional="len($df1$) > 1",
    )

    assert set(widget.dependencies()) == {"df1"}

    widget = CsvReader(
        key="CsvReader",
        value=None,
        optional=True,
        count="len($df1$)"
    )

    assert set(widget.dependencies()) == {"df1"}
