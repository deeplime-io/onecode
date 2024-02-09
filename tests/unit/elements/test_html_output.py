import json
import os
import shutil

from onecode import Env, HtmlOutput, Mode, Project
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_console_html_output():
    Project().mode = Mode.CONSOLE

    widget = HtmlOutput(
        key="HtmlOutput",
        value="my_file.html",
        tags=["Core"],
        metadata="data"
    )

    assert type(widget()) == HtmlOutput
    assert widget.metadata == "data"
    assert widget.kind == "HtmlOutput"


def test_execute_html_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = HtmlOutput(
        key="HtmlOutput",
        value="my_file.html",
        tags=["Core"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.html')
    assert widget.key == "htmloutput"
    assert widget.label == "'''HtmlOutput'''"
    assert widget._label == "HtmlOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "htmloutput",
            "label": "HtmlOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.html'),
            "tags": ["Core"],
            "kind": "HtmlOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_html_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().current_flow = flow_id

    widget = HtmlOutput(
        key="HtmlOutput",
        value="my_file.html",
        tags=["Core"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.html')
    assert widget.key == "htmloutput"
    assert widget.label == "'''HtmlOutput'''"
    assert widget._label == "HtmlOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "htmloutput",
            "label": "HtmlOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.html'),
            "tags": ["Core"],
            "kind": "HtmlOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_extract_html_output():
    Project().mode = Mode.EXTRACT

    widget = HtmlOutput(
        key="HtmlOutput",
        value="my_file.html",
        tags=["Core"]
    )

    assert widget() is None


def test_extract_all_html_output():
    Project().mode = Mode.EXTRACT_ALL

    widget = HtmlOutput(
        key="HtmlOutput",
        value="my_file.html",
        tags=["Core"]
    )

    assert widget() is None
