import json
import os
import shutil

import pytest

from onecode import Env
from onecode.cli.add import add
from onecode.cli.create import create
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_add_success():
    flow_name, flow_folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(flow_name)

    create(tmp, flow_folder, cli=False)
    add(os.path.join(tmp, flow_folder), 'New Flow', cli=False)

    assert os.path.exists(os.path.join(tmp, flow_folder, 'flows', 'new_flow.py'))

    try:
        shutil.rmtree(os.path.join(tmp, flow_folder))
    except Exception:
        pass


def test_add_failure_not_a_flow():
    with pytest.raises(FileNotFoundError) as excinfo:
        add('My OneCode', 'New Flow', cli=False)

    assert "Hmmm, it doesn't look like this is a OneCode project (config file not found)" == \
        str(excinfo.value)


def test_add_failure_existing_flow():
    flow_name, flow_folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(flow_folder)

    create(tmp, flow_name, cli=False)
    add(os.path.join(tmp, flow_folder), 'New Flow', cli=False)

    with pytest.raises(ValueError) as excinfo:
        add(os.path.join(tmp, flow_folder), 'New Flow', cli=False)

    assert "Flow New Flow is already registered, please pick another name" == \
        str(excinfo.value)

    try:
        shutil.rmtree(os.path.join(tmp, flow_folder))
    except Exception:
        pass


def test_add_failure_empty_flow_name():
    flow_name, flow_folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(flow_folder)

    create(tmp, flow_name, cli=False)

    with pytest.raises(ValueError) as excinfo:
        add(os.path.join(tmp, flow_folder), '', cli=False)

    assert "Empty flow name" == str(excinfo.value)

    try:
        shutil.rmtree(os.path.join(tmp, flow_folder))
    except Exception:
        pass


def test_config_file_content():
    flow_name, flow_folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(flow_folder)

    create(tmp, flow_name, cli=False)
    add(os.path.join(tmp, flow_folder), 'New Flow', cli=False)

    with open(os.path.join(tmp, flow_folder, Env.ONECODE_CONFIG_FILE)) as f:
        flows = json.load(f)

    assert flows == [
        {"file": flow_id, "label": flow_name, "attributes": {}},
        {"file": "new_flow", "label": "New Flow", "attributes": {}}
    ]

    try:
        shutil.rmtree(os.path.join(tmp, flow_folder))
    except Exception:
        pass


def test_add_before():
    flow_name, flow_folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(flow_folder)

    create(tmp, flow_name, cli=False)

    # put new flow before
    add(os.path.join(tmp, flow_folder), 'New Flow', flow_id, False)
    with open(os.path.join(tmp, flow_folder, Env.ONECODE_CONFIG_FILE)) as f:
        flows = json.load(f)

    assert flows == [
        {"file": "new_flow", "label": "New Flow", "attributes": {}},
        {"file": flow_id, "label": flow_name, "attributes": {}}
    ]

    # should put it at the end as no flow doesn't exist
    add(os.path.join(tmp, flow_folder), 'Another Flow', 'no flow', False)
    with open(os.path.join(tmp, flow_folder, Env.ONECODE_CONFIG_FILE)) as f:
        flows = json.load(f)

    assert flows == [
        {"file": "new_flow", "label": "New Flow", "attributes": {}},
        {"file": flow_id, "label": flow_name, "attributes": {}},
        {"file": "another_flow", "label": "Another Flow", "attributes": {}}
    ]

    # should put it after My OneCode
    add(os.path.join(tmp, flow_folder), 'Yet Another Flow', flow_id, False)
    with open(os.path.join(tmp, flow_folder, Env.ONECODE_CONFIG_FILE)) as f:
        flows = json.load(f)

    assert flows == [
        {"file": "new_flow", "label": "New Flow", "attributes": {}},
        {"file": "yet_another_flow", "label": "Yet Another Flow", "attributes": {}},
        {"file": flow_id, "label": flow_name, "attributes": {}},
        {"file": "another_flow", "label": "Another Flow", "attributes": {}}
    ]

    try:
        shutil.rmtree(os.path.join(tmp, flow_folder))
    except Exception:
        pass
