import json
import os
import shutil

import pytest

from onecode import Env, Mode, PyvistaVrmlOutput, Project
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_console_pyvista_vrml_output():
    Project().mode = Mode.CONSOLE

    widget = PyvistaVrmlOutput(
        key="PyvistaVrmlOutput",
        value="my_file.vrml",
        tags=["VRML"],
        metadata="data"
    )

    assert type(widget()) == PyvistaVrmlOutput
    assert widget.metadata == "data"
    assert widget.kind == "PyvistaVrmlOutput"


def test_execute_pyvista_vrml_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = PyvistaVrmlOutput(
        key="PyvistaVrmlOutput",
        value="my_file.vrml",
        tags=["VRML"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.vrml')
    assert widget.key == "pyvistavrmloutput"
    assert widget.label == "'''PyvistaVrmlOutput'''"
    assert widget._label == "PyvistaVrmlOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "pyvistavrmloutput",
            "label": "PyvistaVrmlOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.vrml'),
            "tags": ["VRML"],
            "kind": "PyvistaVrmlOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_pyvista_vrml_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().current_flow = flow_id

    widget = PyvistaVrmlOutput(
        key="PyvistaVrmlOutput",
        value="my_file.vrml",
        tags=["VRML"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.vrml')
    assert widget.key == "pyvistavrmloutput"
    assert widget.label == "'''PyvistaVrmlOutput'''"
    assert widget._label == "PyvistaVrmlOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "pyvistavrmloutput",
            "label": "PyvistaVrmlOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.vrml'),
            "tags": ["VRML"],
            "kind": "PyvistaVrmlOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_extension_pyvista_vrml_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = PyvistaVrmlOutput(
        key="PyvistaVrmlOutput",
        value="my_file.txt",
        tags=["VRML"]
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[pyvistavrmloutput] Invalid VRML extension: .txt (accepted: .vrml)" == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_extract_pyvista_vrml_output():
    Project().mode = Mode.EXTRACT

    widget = PyvistaVrmlOutput(
        key="PyvistaVrmlOutput",
        value="my_file.vrml",
        tags=["VRML"]
    )

    assert widget() is None


def test_extract_all_pyvista_vrml_output():
    Project().mode = Mode.EXTRACT_ALL

    widget = PyvistaVrmlOutput(
        key="PyvistaVrmlOutput",
        value="my_file.vrml",
        tags=["VRML"]
    )

    assert widget() is None
