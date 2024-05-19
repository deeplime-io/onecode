import json
import os
import shutil

from onecode import Env, FileOutput, Mode, Project
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_console_file_output():
    Project().mode = Mode.CONSOLE

    widget = FileOutput(
        key="FileOutput",
        value="my_file.txt",
        tags=["Core"],
        testdata="data"
    )

    assert type(widget()) == FileOutput
    assert widget.testdata == "data"
    assert widget.kind == "FileOutput"
    assert widget.mimetype == "text/plain"


def test_execute_file_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = FileOutput(
        key="FileOutput",
        value="my_file.jpg",
        tags=["Image"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.jpg')
    assert widget.key == "fileoutput"
    assert widget.label == "FileOutput"
    assert widget._label == "FileOutput"
    assert widget.mimetype == "image/jpeg"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "fileoutput",
            "label": "FileOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.jpg'),
            "tags": ["Image"],
            "mimetype": 'image/jpeg',
            "kind": "FileOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_file_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().current_flow = flow_id

    widget = FileOutput(
        key="FileOutput",
        value="my_file.txt",
        tags=["Core"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.txt')
    assert widget.key == "fileoutput"
    assert widget.label == "FileOutput"
    assert widget._label == "FileOutput"
    assert widget.mimetype == "text/plain"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "fileoutput",
            "label": "FileOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.txt'),
            "tags": ["Core"],
            "mimetype": 'text/plain',
            "kind": "FileOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_extract_file_output():
    Project().mode = Mode.EXTRACT

    widget = FileOutput(
        key="FileOutput",
        value="my_file.txt",
        tags=["Core"]
    )

    assert widget() is None


def test_extract_all_file_output():
    Project().mode = Mode.EXTRACT_ALL

    widget = FileOutput(
        key="FileOutput",
        value="my_file.txt",
        tags=["Core"]
    )

    assert widget() is None
