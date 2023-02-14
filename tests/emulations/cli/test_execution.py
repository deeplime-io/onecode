import json
import os
import shutil

import pytest

from onecode import Env
from onecode.cli.add import add
from onecode.cli.create import create
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


@pytest.mark.emulations
def test_single_flow_execution():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'w') as f:
        f.write("Flow just executed!")
""")

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "Flow just executed!"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_multiple_flows_execution():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    flow_dir = os.path.join(tmp, flow_folder)

    create(tmp, flow_name, cli=False)
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 3 just executed!")
""")

    add(os.path.join(tmp, flow_folder), 'New Flow', flow_id, False)
    with open(os.path.join(flow_dir, 'flows', 'new_flow.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 1 just executed!")
""")

    add(os.path.join(tmp, flow_folder), 'Another Flow', 'no flow', False)
    with open(os.path.join(flow_dir, 'flows', 'another_flow.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 4 just executed!")
""")

    add(os.path.join(tmp, flow_folder), 'Yet Another Flow', flow_id, False)
    with open(os.path.join(flow_dir, 'flows', 'yet_another_flow.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 2 just executed!")
""")

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == (
            "Flow 1 just executed!"
            "Flow 2 just executed!"
            "Flow 3 just executed!"
            "Flow 4 just executed!"
        )

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_single_flow_execution_in_multi_flows():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    flow_dir = os.path.join(tmp, flow_folder)

    create(tmp, flow_name, cli=False)
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 3 just executed!")
""")

    add(os.path.join(tmp, flow_folder), 'New Flow', flow_id, False)
    with open(os.path.join(flow_dir, 'flows', 'new_flow.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 1 just executed!")
""")

    add(os.path.join(tmp, flow_folder), 'Another Flow', 'no flow', False)
    with open(os.path.join(flow_dir, 'flows', 'another_flow.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 4 just executed!")
""")

    add(os.path.join(tmp, flow_folder), 'Yet Another Flow', flow_id, False)
    with open(os.path.join(flow_dir, 'flows', 'yet_another_flow.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 2 just executed!")
""")

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py --flow another_flow')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == (
            "Flow 4 just executed!"
        )

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_single_flow_execution_in_multi_flows_with_params():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    flow_dir = os.path.join(tmp, flow_folder)

    create(tmp, flow_name, cli=False)
    with open(os.path.join(flow_dir, 'params.json'), 'w') as f:
        json.dump({"my_var": 15.6}, f)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 3 just executed!")
""")

    add(os.path.join(tmp, flow_folder), 'New Flow', flow_id, False)
    with open(os.path.join(flow_dir, 'flows', 'new_flow.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 1 just executed!")
""")

    add(os.path.join(tmp, flow_folder), 'Another Flow', 'no flow', False)
    with open(os.path.join(flow_dir, 'flows', 'another_flow.py'), 'a') as f:
        f.write("""
    x = onecode.slider("my_var", 12.3, min=12, max=16, step=0.1)

    with open("stdout.txt", 'a') as f:
        f.write(f"Flow {x} just executed!")
""")

    add(os.path.join(tmp, flow_folder), 'Yet Another Flow', flow_id, False)
    with open(os.path.join(flow_dir, 'flows', 'yet_another_flow.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'a') as f:
        f.write("Flow 2 just executed!")
""")

    os.system(
        f'cd "{flow_dir}" && '
        f'{Env.ONECODE_DO_TYPECHECK}=1 python main.py --flow another_flow params.json'
    )

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == (
            "Flow 15.6 just executed!"
        )

    shutil.rmtree(flow_dir)
