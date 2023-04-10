import os
import shutil

import pytest

from onecode import FileFilter, FileInput, Mode, Project
from tests.utils.flow_cli import (
    _clean_flow,
    _generate_csv_file,
    _generate_flow_name
)
from tests.utils.format import strip


def test_console_single_file_input():
    Project().mode = Mode.CONSOLE

    widget = FileInput(
        key="FileInput",
        value=None,
        optional=True,
        metadata="data"
    )

    assert type(widget()) == FileInput
    assert widget.metadata == "data"
    assert widget.kind == "FileInput"


def test_execute_single_file_input_single_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=csv_file
    )

    assert widget() == csv_file
    assert widget.key == "fileinput"
    assert widget.label == "'''FileInput'''"
    assert widget._label == "FileInput"

    widget = FileInput(
        key="FileInput",
        value="test.csv"
    )

    assert widget() == os.path.join(folder_path, 'data', 'test.csv')

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_single_file_input_multiple_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=[csv_file],
        multiple=True
    )

    assert widget() == [csv_file]
    assert widget.key == "fileinput"
    assert widget.label == "'''FileInput'''"
    assert widget._label == "FileInput"

    widget = FileInput(
        key="FileInput",
        value=["test.csv"],
        multiple=True
    )

    assert widget() == [os.path.join(folder_path, 'data', 'test.csv')]

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_multiple_file_input_single_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file_1 = _generate_csv_file(folder_path, 'test1.csv')
    csv_file_2 = _generate_csv_file(folder_path, 'test2.csv')

    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=[csv_file_1, csv_file_2],
        count=2
    )

    assert widget() == [
        os.path.join(folder_path, 'data', 'test1.csv'),
        os.path.join(folder_path, 'data', 'test2.csv')
    ]

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_multiple_file_input_multiple_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file_1 = _generate_csv_file(folder_path, 'test1.csv')
    csv_file_2 = _generate_csv_file(folder_path, 'test2.csv')

    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=[[csv_file_1, csv_file_2]],
        multiple=True,
        count=2
    )

    assert widget() == [[
        os.path.join(folder_path, 'data', 'test1.csv'),
        os.path.join(folder_path, 'data', 'test2.csv')
    ]]

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_optional_file_input_single_selection():
    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=None,
        optional=True
    )

    assert widget() is None


def test_execute_optional_file_input_multiple_selection():
    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=None,
        optional=True,
        multiple=True
    )

    assert widget() is None


def test_execute_invalid_path_file_input_single_selection():
    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value="nofile.csv"
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        widget()

    assert f"[fileinput] File not found: {os.path.join(os.getcwd(), 'nofile.csv')}" == \
        str(excinfo.value)


def test_execute_invalid_path_file_input_multiple_selection():
    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=["nofile.csv"],
        multiple=True
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        widget()

    assert f"[fileinput] File not found: {os.path.join(os.getcwd(), 'nofile.csv')}" == \
        str(excinfo.value)


def test_execute_invalid_dir_file_input_single_selection():
    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value="tests"
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        widget()

    assert f"[fileinput] Path is not a file: {os.path.join(os.getcwd(), 'tests')}" == \
        str(excinfo.value)


def test_execute_invalid_dir_file_input_multiple_selection():
    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=["tests"],
        multiple=True
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        widget()

    assert f"[fileinput] Path is not a file: {os.path.join(os.getcwd(), 'tests')}" == \
        str(excinfo.value)


def test_execute_invalid_single_file_input_single_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=csv_file,
        count=1
    )
    with pytest.raises(TypeError) as excinfo:
        widget()

    assert f"Invalid value {csv_file}, expected: list(<class 'str'>)" == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_single_file_input_multiple_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=[csv_file],
        count=1,
        multiple=True
    )
    with pytest.raises(TypeError) as excinfo:
        widget()

    assert f"Invalid value type for each element of {[csv_file]}, expected: typing.List[str]" == \
        str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_multiple_file_input_single_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file_1 = _generate_csv_file(folder_path, 'test1.csv')
    csv_file_2 = _generate_csv_file(folder_path, 'test2.csv')

    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=[csv_file_1, csv_file_2],
        count=None
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    # welcome to Windows world...
    if os.name == 'nt':
        csv_file_1 = csv_file_1.replace('\\', '\\\\')
        csv_file_2 = csv_file_2.replace('\\', '\\\\')

    assert f"Invalid value type for ['{csv_file_1}', '{csv_file_2}'], expected: <class 'str'>" == \
        str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_multiple_file_input_multiple_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file_1 = _generate_csv_file(folder_path, 'test1.csv')
    csv_file_2 = _generate_csv_file(folder_path, 'test2.csv')

    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=[[csv_file_1, csv_file_2]],
        multiple=True,
        count=None
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    # welcome to Windows world...
    if os.name == 'nt':
        csv_file_1 = csv_file_1.replace('\\', '\\\\')
        csv_file_2 = csv_file_2.replace('\\', '\\\\')

    assert strip(
        f"Invalid value type for [['{csv_file_1}', '{csv_file_2}']], expected: typing.List[str]"
    ) == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_optional_file_input():
    Project().mode = Mode.EXECUTE

    widget = FileInput(
        key="FileInput",
        value=None
    )

    assert widget.value is None

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[fileinput] Value is required: None provided" == str(excinfo.value)


def test_extract_all_file_input():
    Project().mode = Mode.EXTRACT_ALL

    widget = FileInput(
        key="FileInput",
        value=["/path/to/file.jpg"],
        label="My FileInput",
        optional="$x$",
        count=2,
        multiple=True,
        tags=["Core"],
        types=[FileFilter.IMAGE]
    )

    assert widget() == ('fileinput', {
        "key": "fileinput",
        "kind": "FileInput",
        "value": ["/path/to/file.jpg"],
        "label": "My FileInput",
        "disabled": '_DATA_["x"]',
        "optional": True,
        "count": "2",
        "tags": ["Core"],
        "types": [("Image", ".jpg .png .jpeg")],
        "multiple": True
    })


def test_extract_all_file_input_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "fileinput": "/file.png"
    }

    widget = FileInput(
        key="FileInput",
        value=["/path/to/file.jpg"],
        label="My FileInput",
        optional="$x$",
        count=2,
        multiple=True,
        tags=["Core"],
        types=[FileFilter.IMAGE]
    )

    assert widget() == ('fileinput', {
        "key": "fileinput",
        "kind": "FileInput",
        "value": "/file.png",
        "label": "My FileInput",
        "disabled": '_DATA_["x"]',
        "optional": True,
        "count": "2",
        "tags": ["Core"],
        "types": [("Image", ".jpg .png .jpeg")],
        "multiple": True
    })


def test_load_then_execute_file_input():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "fileinput": csv_file
    }

    widget = FileInput(
        key="FileInput",
        value=None,
        optional=True
    )

    assert widget() == csv_file
    assert widget.key == "fileinput"
    assert widget.label == "'''FileInput'''"
    assert widget._label == "FileInput"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_file_input_no_key():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file = _generate_csv_file(folder_path, 'test.csv')

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_fileinput": csv_file
    }

    widget = FileInput(
        key="FileInput",
        value=None,
        optional=True
    )

    assert widget() is None
    assert widget.key == "fileinput"
    assert widget.label == "'''FileInput'''"
    assert widget._label == "FileInput"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass
