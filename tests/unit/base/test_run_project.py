import os
import shutil

from onecode import Env
from onecode.cli.create import create
from tests.utils.flow_cli import _clean_flow, _generate_flow_name, run_project


def test_default_data_path():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'w') as f:
        f.write(onecode.Project().data_root)
    """)

    run_project(flow_dir)

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == flow_data

    shutil.rmtree(flow_dir)


def test_env_data_path():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    with open("stdout.txt", 'w') as f:
        f.write(onecode.Project().data_root)
    """)

    os.environ[Env.ONECODE_PROJECT_DATA] = flow_data
    run_project(flow_dir)

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == flow_data

    shutil.rmtree(os.path.join(tmp, flow_folder))


def test_output_multiprocess():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')

    with open(os.path.join(flow_dir, 'flows', 'utils.py'), 'w') as f:
        f.write("""
import onecode


def write_output(data, flow_name):
    onecode.Project().current_flow = flow_name
    onecode.Project().write_output({data: '0'})
    """)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'w') as f:
        f.write("""
from multiprocessing import Process
from flows.utils import write_output
import onecode


def run():
    names = ['b', 'a', 'c'] * 10
    procs = []
    parent_flow = onecode.Project().current_flow

    for name in names:
        proc = Process(target=write_output, args=(name, parent_flow))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()
    """)

    os.environ[Env.ONECODE_PROJECT_DATA] = flow_data
    run_project(flow_dir)

    with open(os.path.join(flow_data, 'outputs', flow_id, 'MANIFEST.txt')) as f:
        data = f.read()

    assert data.count('a') == 10
    assert data.count('b') == 10
    assert data.count('c') == 10
    assert data.count('0') == 30

    shutil.rmtree(os.path.join(tmp, flow_folder))


def test_manifest_cleaning():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')

    with open(os.path.join(flow_dir, 'flows', 'utils.py'), 'w') as f:
        f.write("""
import onecode


def write_output(data, flow_name):
    onecode.Project().current_flow = flow_name
    onecode.Project().write_output({data: '0'})
    """)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'w') as f:
        f.write("""
from multiprocessing import Process
from flows.utils import write_output
import onecode


def run():
    names = ['b', 'a', 'c'] * 10
    procs = []
    parent_flow = onecode.Project().current_flow

    for name in names:
        proc = Process(target=write_output, args=(name, parent_flow))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()
    """)

    os.environ[Env.ONECODE_PROJECT_DATA] = flow_data
    run_project(flow_dir)
    run_project(flow_dir)
    run_project(flow_dir)

    with open(os.path.join(flow_data, 'outputs', flow_id, 'MANIFEST.txt')) as f:
        data = f.read()

    assert data.count('a') == 10
    assert data.count('b') == 10
    assert data.count('c') == 10
    assert data.count('0') == 30

    shutil.rmtree(os.path.join(tmp, flow_folder))
