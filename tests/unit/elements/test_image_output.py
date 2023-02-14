import json
import os
import shutil

import pytest

from onecode import Env, ImageOutput, Mode, Project
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_console_image_output():
    Project().mode = Mode.CONSOLE

    widget = ImageOutput(
        key="ImageOutput",
        value="my_file.jpg",
        tags=["Image"]
    )

    assert type(widget()) == ImageOutput


def test_execute_image_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = ImageOutput(
        key="ImageOutput",
        value="my_file.jpg",
        tags=["Image"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.jpg')
    assert widget.key == "imageoutput"
    assert widget.label == "'''ImageOutput'''"
    assert widget._label == "ImageOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "imageoutput",
            "label": "ImageOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.jpg'),
            "tags": ["Image"],
            "kind": "ImageOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_load_then_execute_image_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().current_flow = flow_id

    widget = ImageOutput(
        key="ImageOutput",
        value="my_file.jpg",
        tags=["Image"]
    )

    assert widget() == os.path.join(data_path, 'outputs', 'my_file.jpg')
    assert widget.key == "imageoutput"
    assert widget.label == "'''ImageOutput'''"
    assert widget._label == "ImageOutput"

    with open(os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt'), 'r') as f:
        assert json.loads(f.read()) == {
            "key": "imageoutput",
            "label": "ImageOutput",
            "value": os.path.join(data_path, 'outputs', 'my_file.jpg'),
            "tags": ["Image"],
            "kind": "ImageOutput"
        }

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_execute_invalid_extension_image_output():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')
    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    widget = ImageOutput(
        key="ImageOutput",
        value="my_file.txt",
        tags=["Image"]
    )

    with pytest.raises(ValueError) as excinfo:
        widget()

    assert "[imageoutput] Invalid image extension: .txt (accepted: .jpg, .jpeg, .png, .svg)" == \
        str(excinfo.value)

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_extract_image_output():
    Project().mode = Mode.EXTRACT

    widget = ImageOutput(
        key="ImageOutput",
        value="my_file.jpg",
        tags=["Image"]
    )

    assert widget() is None


def test_extract_all_image_output():
    Project().mode = Mode.EXTRACT_ALL

    widget = ImageOutput(
        key="ImageOutput",
        value="my_file.jpg",
        tags=["Image"]
    )

    assert widget() is None
