import json
import os
import shutil

import pytest
from slugify import slugify

from onecode import Env
from onecode.cli.create import create
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_create_success():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    assert os.path.exists(os.path.join(tmp, flow_folder, 'flows', f'{flow_id}.py'))
    assert os.path.exists(os.path.join(tmp, flow_folder, 'flows', 'onecode_ext', '__init__.py'))
    assert os.path.exists(os.path.join(
        tmp,
        flow_folder,
        'flows',
        'onecode_ext',
        'input_elements',
        '__init__.py')
    )
    assert os.path.exists(os.path.join(
        tmp,
        flow_folder,
        'flows',
        'onecode_ext',
        'output_elements',
        '__init__.py')
    )

    try:
        shutil.rmtree(os.path.join(tmp, flow_folder))
    except Exception:
        pass


def test_create_with_main_flow_success():
    flow_name, flow_folder, _ = _generate_flow_name()
    main_flow = "Main Flow"
    flow_id = slugify(main_flow, separator='_')

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, main_flow, cli=False)

    assert os.path.exists(os.path.join(tmp, flow_folder, 'flows', f'{flow_id}.py'))
    assert os.path.exists(os.path.join(tmp, flow_folder, 'flows', 'onecode_ext', '__init__.py'))
    assert os.path.exists(os.path.join(
        tmp,
        flow_folder,
        'flows',
        'onecode_ext',
        'input_elements',
        '__init__.py')
    )
    assert os.path.exists(os.path.join(
        tmp,
        flow_folder,
        'flows',
        'onecode_ext',
        'output_elements',
        '__init__.py')
    )

    try:
        shutil.rmtree(os.path.join(tmp, flow_folder))
    except Exception:
        pass


def test_create_failure_existing_flow():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    with pytest.raises(FileExistsError) as excinfo:
        create(tmp, flow_name, cli=False)

    assert \
        f"A file or a directory with the path {os.path.join(tmp, flow_folder)} already exists" == \
        str(excinfo.value)

    try:
        shutil.rmtree(os.path.join(tmp, flow_folder))
    except Exception:
        pass


def test_config_file_content():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    with open(os.path.join(tmp, flow_folder, Env.ONECODE_CONFIG_FILE)) as f:
        flows = json.load(f)

    assert flows == [{"file": flow_id, "label": flow_name, "attributes": {}}]

    try:
        shutil.rmtree(os.path.join(tmp, flow_folder))
    except Exception:
        pass
