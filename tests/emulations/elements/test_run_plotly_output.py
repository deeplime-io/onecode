import json
import os
import shutil

import pytest

from onecode import Env
from onecode.cli.create import create
from tests.utils.flow_cli import _clean_flow, _generate_flow_name
from tests.utils.format import strip


@pytest.mark.emulations
def test_execute():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.plotly_output('My Plotly Output', 'test_file.json', label=None, tags=['JSON', 'Core'])
    with open("stdout.txt", 'w') as f:
        f.write(x)
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"{flow_data}/outputs/test_file.json"

    with open(os.path.join(flow_data, "outputs", flow_id, "MANIFEST.txt")) as f:
        assert json.loads(f.read()) == {
            "key": "my_plotly_output",
            "label": "My Plotly Output",
            "value": f"{flow_data}/outputs/test_file.json",
            "tags": ["JSON", "Core"],
            "kind": "PlotlyOutput"
        }

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_invalid_execute():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.plotly_output('my_plotly_output', 'test_file.plot', tags=['JSON', 'Core'])
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == strip("""
            [my_plotly_output] Invalid Plotly extension:
            .plot (accepted: .json)
        """)

    assert not os.path.exists(os.path.join(flow_data, "outputs", flow_id, "MANIFEST.txt"))

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_invalid_name_key():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.plotly_output('_my_plotly_output', 'test_file.json', tags=['JSON', 'Core'])
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == 'Key starting with "_" are reserved: _my_plotly_output'

    shutil.rmtree(flow_dir)
