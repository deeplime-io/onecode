import json
import os
import shutil

import pytest

from onecode import Env, Mode, PlotlyOutput, Project
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_console_plotly_output():
    Project().mode = Mode.CONSOLE

    widget = PlotlyOutput(
        key="PlotlyOutput",
        value="my_file.json",
        tags=["JSON"],
        metadata="data"
    )

    assert type(widget()) == PlotlyOutput
    assert widget.metadata == "data"
    assert widget.kind == "PlotlyOutput"


def test_execute_plotly_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = PlotlyOutput(
        key="PlotlyOutput",
        value="my_file.json",
        tags=["JSON"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.json')
    assert widget.key == "plotlyoutput"
    assert widget.label == "PlotlyOutput"
    assert widget._label == "PlotlyOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "plotlyoutput",
            "label": "PlotlyOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.json'),
            "tags": ["JSON"],
            "kind": "PlotlyOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_plotly_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().current_flow = flow_id

    widget = PlotlyOutput(
        key="PlotlyOutput",
        value="my_file.json",
        tags=["JSON"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.json')
    assert widget.key == "plotlyoutput"
    assert widget.label == "PlotlyOutput"
    assert widget._label == "PlotlyOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "plotlyoutput",
            "label": "PlotlyOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.json'),
            "tags": ["JSON"],
            "kind": "PlotlyOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_extension_plotly_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = PlotlyOutput(
        key="PlotlyOutput",
        value="my_file.txt",
        tags=["JSON"]
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[plotlyoutput] Invalid Plotly extension: .txt (accepted: .json)" == str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_extract_plotly_output():
    Project().mode = Mode.EXTRACT

    widget = PlotlyOutput(
        key="PlotlyOutput",
        value="my_file.json",
        tags=["JSON"]
    )

    assert widget() is None


def test_extract_all_plotly_output():
    Project().mode = Mode.EXTRACT_ALL

    widget = PlotlyOutput(
        key="PlotlyOutput",
        value="my_file.json",
        tags=["JSON"]
    )

    assert widget() is None
