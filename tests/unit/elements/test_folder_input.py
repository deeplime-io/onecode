import os
import shutil

import pytest

from onecode import FolderInput, Mode, Project
from tests.utils.flow_cli import (
    _clean_flow,
    _generate_flow_name,
    _generate_folder
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

    test_folder = _generate_folder(folder_path)

    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=test_folder
    )

    assert widget() == test_folder
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
    folder_path = os.path.join(tmp, folder)

    test_folder_1 = _generate_folder(f"{folder_path}_1")
    test_folder_2 = _generate_folder(f"{folder_path}_2")

    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=[test_folder_1, test_folder_2],
        count=2
    )

    assert widget() == [
        f"{folder_path}_1",
        f"{folder_path}_2"
    ]

    try:
        shutil.rmtree(folder_path)
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


def test_execute_invalid_path_file_input_single_selection():
    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value="nofolder"
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        widget()

    assert f"[folderinput] Folder not found: {os.path.join(os.getcwd(), 'nofolder')}" == \
        str(excinfo.value)


def test_execute_invalid_single_file_input_single_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    test_folder = _generate_folder(folder_path)

    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=test_folder,
        count=1
    )
    with pytest.raises(TypeError) as excinfo:
        widget()

    assert f"Invalid value {test_folder}, expected: list(<class 'str'>)" == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_multiple_file_input_single_selection():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    test_folder_1 = _generate_folder(folder_path)
    test_folder_2 = _generate_folder(folder_path)

    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=[test_folder_1, test_folder_2],
        count=None
    )

    with pytest.raises(TypeError) as excinfo:
        widget()

    # welcome to Windows world...
    if os.name == 'nt':
        test_folder_1 = test_folder_1.replace('\\', '\\\\')
        test_folder_2 = test_folder_2.replace('\\', '\\\\')

    assert strip(
        f"Invalid value type for ['{test_folder_1}', '{test_folder_2}'], expected: <class 'str'>"
     ) == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_optional_file_input():
    Project().mode = Mode.EXECUTE

    widget = FolderInput(
        key="FolderInput",
        value=None
    )

    assert widget.value is None

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[folderinput] Value is required: None provided" == str(excinfo.value)


def test_extract_all_file_input():
    Project().mode = Mode.EXTRACT_ALL

    widget = FolderInput(
        key="FolderInput",
        value=["/path/to"],
        label="My FolderInput",
        optional="$x$",
        count=2,
        tags=["Core"],
    )

    assert widget() == ('folderinput', {
        "key": "folderinput",
        "kind": "FolderInput",
        "value": ["/path/to"],
        "label": "My FolderInput",
        "disabled": '_DATA_["x"]',
        "optional": True,
        "count": "2",
        "tags": ["Core"]
    })


def test_extract_all_file_input_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "folderinput": "/"
    }

    widget = FolderInput(
        key="FolderInput",
        value=["/path/to"],
        label="My FolderInput",
        optional="$x$",
        count=2,
        tags=["Core"]
    )

    assert widget() == ('folderinput', {
        "key": "folderinput",
        "kind": "FolderInput",
        "value": "/",
        "label": "My FolderInput",
        "disabled": '_DATA_["x"]',
        "optional": True,
        "count": "2",
        "tags": ["Core"]
    })


def test_load_then_execute_file_input():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    test_folder = _generate_folder(folder_path)

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "folderinput": test_folder
    }

    widget = FolderInput(
        key="FolderInput",
        value=None,
        optional=True
    )

    assert widget() == test_folder
    assert widget.key == "folderinput"
    assert widget.label == "'''FolderInput'''"
    assert widget._label == "FolderInput"

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_file_input_no_key():
    _, folder, _ = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)

    test_folder = _generate_folder(folder_path)

    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_folderinput": test_folder
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
