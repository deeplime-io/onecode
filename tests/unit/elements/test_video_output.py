import json
import os
import shutil

import pytest

from onecode import Env, Mode, Project, VideoOutput
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_console_video_output():
    Project().mode = Mode.CONSOLE

    widget = VideoOutput(
        key="VideoOutput",
        value="my_file.mp4",
        tags=["Video"],
        metadata="data"
    )

    assert type(widget()) == VideoOutput
    assert widget.metadata == "data"
    assert widget.kind == "VideoOutput"


def test_execute_video_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = VideoOutput(
        key="VideoOutput",
        value="my_file.mp4",
        tags=["Video"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.mp4')
    assert widget.key == "videooutput"
    assert widget.label == "'''VideoOutput'''"
    assert widget._label == "VideoOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "videooutput",
            "label": "VideoOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.mp4'),
            "tags": ["Video"],
            "kind": "VideoOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_video_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().current_flow = flow_id

    widget = VideoOutput(
        key="VideoOutput",
        value="my_file.mp4",
        tags=["Video"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.mp4')
    assert widget.key == "videooutput"
    assert widget.label == "'''VideoOutput'''"
    assert widget._label == "VideoOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "videooutput",
            "label": "VideoOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.mp4'),
            "tags": ["Video"],
            "kind": "VideoOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_extension_video_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = VideoOutput(
        key="VideoOutput",
        value="my_file.txt",
        tags=["Video"]
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[videooutput] Invalid video extension: .txt (accepted: .mp4)" == \
        str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_extract_video_output():
    Project().mode = Mode.EXTRACT

    widget = VideoOutput(
        key="VideoOutput",
        value="my_file.mp4",
        tags=["Video"]
    )

    assert widget() is None


def test_extract_all_video_output():
    Project().mode = Mode.EXTRACT_ALL

    widget = VideoOutput(
        key="VideoOutput",
        value="my_file.mp4",
        tags=["Video"]
    )

    assert widget() is None
