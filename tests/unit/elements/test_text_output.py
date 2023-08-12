import json
import os
import shutil

from onecode import Env, Mode, Project, TextOutput
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_console_text_output():
    Project().mode = Mode.CONSOLE

    widget = TextOutput(
        key="TextOutput",
        value="my_file.txt",
        tags=["Core"],
        truncate_at=25000,
        metadata="data"
    )

    assert type(widget()) == TextOutput
    assert widget.metadata == "data"
    assert widget.kind == "TextOutput"


def test_execute_text_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = TextOutput(
        key="TextOutput",
        value="my_file.txt",
        tags=["Core"],
        truncate_at=25000
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.txt')
    assert widget.key == "textoutput"
    assert widget.label == "TextOutput"
    assert widget._label == "TextOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "textoutput",
            "label": "TextOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.txt'),
            "tags": ["Core"],
            "kind": "TextOutput",
            "truncate_at": 25000
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_text_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().current_flow = flow_id

    widget = TextOutput(
        key="TextOutput",
        value="my_file.txt",
        tags=["Core"],
        truncate_at=25000
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.txt')
    assert widget.key == "textoutput"
    assert widget.label == "TextOutput"
    assert widget._label == "TextOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "textoutput",
            "label": "TextOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.txt'),
            "tags": ["Core"],
            "kind": "TextOutput",
            "truncate_at": 25000
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_extract_text_output():
    Project().mode = Mode.EXTRACT

    widget = TextOutput(
        key="TextOutput",
        value="my_file.txt",
        tags=["Core"],
        truncate_at=25000
    )

    assert widget() is None


def test_extract_all_text_output():
    Project().mode = Mode.EXTRACT_ALL

    widget = TextOutput(
        key="TextOutput",
        value="my_file.txt",
        tags=["Core"],
        truncate_at=25000
    )

    assert widget() is None
