import os
import shutil

import pytest

from onecode import FolderInput, Mode, Project
from tests.utils.flow_cli import (
    _clean_flow,
    _generate_flow_name,
    _generate_csv_file
)
from tests.utils.format import strip


def test_console_single_folder_input():
    Project().mode = Mode.CONSOLE

    widget = FolderInput(
        key="FolderInput",
        value=None,
        optional=True
    )

    assert type(widget()) == FolderInput


def test_execute_folder_input():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    os.makedirs(folder_path, exist_ok=True)

    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=folder_path
    )

    assert widget() == folder_path
    assert widget.key == "folderinput"
    assert widget.label == "'''FolderInput'''"
    assert widget._label == "FolderInput"

    widget = FolderInput(
        key="FolderInput",
        value="/"
    )

    assert widget() == folder_path

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_multiple_folder_input():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path_1 = f"{os.path.join(tmp, folder)}_1"
    folder_path_2 = f"{os.path.join(tmp, folder)}_2"

    os.makedirs(folder_path_1, exist_ok=True)
    os.makedirs(folder_path_2, exist_ok=True)

    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=[folder_path_1, folder_path_2],
        count=2
    )

    assert widget() == [
        folder_path_1,
        folder_path_2
    ]

    try:
        shutil.rmtree(folder_path_1)
        shutil.rmtree(folder_path_2)

    except Exception:
        pass


def test_execute_optional_folder_input_single_selection():
    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=None,
        optional=True
    )

    assert widget() is None


def test_execute_invalid_path_folder_input_single_selection():
    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value="nofolder"
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        widget()

    assert f"[folderinput] Folder not found: {os.path.join(os.getcwd(), 'nofolder')}" == \
        str(excinfo.value)


def test_execute_invalid_type_folder_input_single_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    csv_file_1 = _generate_csv_file(folder_path, 'test1.csv')

    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=csv_file_1
    )

    with pytest.raises(NotADirectoryError) as excinfo:
        widget()

    assert f"[folderinput] Path is not a folder: {os.path.join(folder_path, 'data/test1.csv')}" == \
        str(excinfo.value)


def test_execute_invalid_single_folder_input_single_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    os.makedirs(folder_path, exist_ok=True)

    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=folder_path,
        count=1
    )
    with pytest.raises(TypeError) as excinfo:
        widget()

    assert f"Invalid value {folder_path}, expected: list(<class 'str'>)" == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_multiple_folder_input_single_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path_1 = f"{os.path.join(tmp, folder)}_1"
    folder_path_2 = f"{os.path.join(tmp, folder)}_2"

    os.makedirs(folder_path_1, exist_ok=True)
    os.makedirs(folder_path_2, exist_ok=True)
    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=[folder_path_1, folder_path_2],
        count=None
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    # welcome to Windows world...
    if os.name == 'nt':
        folder_path_1 = folder_path_1.replace('\\', '\\\\')
        folder_path_2 = folder_path_2.replace('\\', '\\\\')

    assert strip(
        f"Invalid value type for ['{folder_path_1}', '{folder_path_2}'], expected: <class 'str'>"
     ) == str(excinfo.value)

    try:
        shutil.rmtree(folder_path_1)
        shutil.rmtree(folder_path_2)
    except Exception:
        pass


def test_execute_invalid_optional_folder_input():
    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=None
    )

    assert widget.value is None

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[folderinput] Value is required: None provided" == str(excinfo.value)


def test_extract_all_folder_input():
    Project().mode = Mode.EXTRACT_ALL

    widget = FolderInput(
        key="FolderInput",
        value=["/path/to"],
        label="My FolderInput",
        optional="$x$",
        count=2
    )

    assert widget() == ('folderinput', {
        "key": "folderinput",
        "kind": "FolderInput",
        "value": ["/path/to"],
        "label": "My FolderInput",
        "disabled": '_DATA_["x"]',
        "optional": True,
        "count": "2"
    })


def test_extract_all_folder_input_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "folderinput": "/"
    }

    widget = FolderInput(
        key="FolderInput",
        value=["/path/to"],
        label="My FolderInput",
        optional="$x$",
        count=2
    )

    assert widget() == ('folderinput', {
        "key": "folderinput",
        "kind": "FolderInput",
        "value": "/",
        "label": "My FolderInput",
        "disabled": '_DATA_["x"]',
        "optional": True,
        "count": "2"
    })


def test_load_then_execute_folder_input():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    os.makedirs(folder_path, exist_ok=True)

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "folderinput": folder_path
    }

    widget = FolderInput(
        key="FolderInput",
        value=None,
        optional=True
    )

    assert widget() == folder_path
    assert widget.key == "folderinput"
    assert widget.label == "'''FolderInput'''"
    assert widget._label == "FolderInput"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_folder_input_no_key():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    os.makedirs(folder_path, exist_ok=True)

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_folderinput": folder_path
    }

    widget = FolderInput(
        key="FolderInput",
        value=None,
        optional=True
    )

    assert widget() is None
    assert widget.key == "folderinput"
    assert widget.label == "'''FolderInput'''"
    assert widget._label == "FolderInput"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass
