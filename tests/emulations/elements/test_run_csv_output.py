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
    x = onecode.csv_output('My CSV Output', 'test_file.csv', label=None, tags=['CSV', 'Core'])
    with open("stdout.txt", 'w') as f:
        f.write(x)
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"{flow_data}/outputs/test_file.csv"

    with open(os.path.join(flow_data, "outputs", flow_id, "MANIFEST.txt")) as f:
        assert json.loads(f.read()) == {
            "key": "my_csv_output",
            "label": "My CSV Output",
            "value": f"{flow_data}/outputs/test_file.csv",
            "tags": ["CSV", "Core"],
            "kind": "CsvOutput"
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
        x = onecode.csv_output('my_csv_output', 'test_file.jxpg', tags=['CSV', 'Core'])
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == strip("""
            [my_csv_output] Invalid CSV extension:
            .jxpg (accepted: .csv)
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
        x = onecode.csv_output('_my_csv_output', 'test_file.csv', tags=['CSV', 'Core'])
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == 'Key starting with "_" are reserved: _my_csv_output'

    shutil.rmtree(flow_dir)
