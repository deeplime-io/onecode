import os
import shutil

import pandas as pd
import pytest

from onecode import CsvReader, Mode, Project
from tests.utils.flow_cli import _clean_flow, _generate_csv_file, _generate_flow_name


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

    assert f"""Invalid value    A  B  C
0  0  1  2
1  3  4  5, expected: list({pd.DataFrame})""" == str(excinfo.value)

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

    assert f"""Invalid value type for [   A  B  C
0  0  1  2
1  3  4  5,    A  B  C
0  0  1  2
1  3  4  5], expected: {pd.DataFrame}""" == str(excinfo.value)

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
        "csv_options": {
            "read_options": {},
            "parse_options": {"delimiter": None},
            "convert_options": {},
        },
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
        "tags": ["CSV"],
        "csv_options": {
            "read_options": {},
            "parse_options": {"delimiter": None},
            "convert_options": {}
        }
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
        "tags": ["CSV"],
        "csv_options": {
            "read_options": {},
            "parse_options": {"delimiter": None},
            "convert_options": {}
        }
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

    assert metadata == {
        ".columns": ["A", "B", "C"],
        "__len__()": 2,
        ".A[]": {
            "unique()": [0, 3],
            "mode()": 0,
            "min()": 0,
            "max()": 3,
            "mean()": 1.5,
            "count()": 2,
            "sum()": 3,
        },
        ".B[]": {
            "unique()": [1, 4],
            "mode()": 1,
            "min()": 1,
            "max()": 4,
            "mean()": 2.5,
            "count()": 2,
            "sum()": 5,
        },
        ".C[]": {
            "unique()": [2, 5],
            "mode()": 2,
            "min()": 2,
            "max()": 5,
            "mean()": 3.5,
            "count()": 2,
            "sum()": 7,
        },
    }

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


def test_csv_reader_metadata_float_and_text(tmp_path):
    csv_file = tmp_path / "mixed.csv"
    csv_file.write_text("name,score\na,1.5\nb,2.5\n")

    metadata = CsvReader.metadata(csv_file)

    assert metadata[".columns"] == ["name", "score"]
    assert metadata["__len__()"] == 2
    assert metadata[".name[]"]["unique()"] == ["a", "b"]
    assert metadata[".name[]"]["mode()"] == "a"
    assert metadata[".name[]"]["min()"] is None
    assert metadata[".name[]"]["sum()"] is None
    assert metadata[".score[]"]["unique()"] is None
    assert metadata[".score[]"]["min()"] == 1.5
    assert metadata[".score[]"]["max()"] == 2.5
    assert metadata[".score[]"]["mean()"] == 2.0
    assert metadata[".score[]"]["sum()"] == 4.0


def test_jsonable_scalar_edges():
    from onecode.elements.input.csv_reader import _jsonable

    assert _jsonable(None) is None

    class BrokenArrow:
        def as_py(self):
            raise RuntimeError("bad scalar")

        def item(self):
            return 4

    assert _jsonable(BrokenArrow()) == 4

    class Missing:
        def as_py(self):
            return float("nan")

    assert _jsonable(Missing()) is None

    class NotScalar:
        def item(self):
            raise ValueError("not a scalar")

    value = NotScalar()
    assert _jsonable(value) is value

    # pd.isna on an array returns an array, which cannot be used as a boolean.
    result = _jsonable(pd.array([1, 2]))
    assert list(result) == [1, 2]
