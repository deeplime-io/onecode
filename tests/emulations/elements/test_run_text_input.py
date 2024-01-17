import json
import os
import shutil

import pytest

from onecode import Env
from onecode.cli.create import create
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


@pytest.mark.emulations
def test_execute_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.text_input('my_text', "OneCode rocks!")
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "OneCode rocks!"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.text_input('my_text', ["OneCode rocks!", "OneCode rocks!"], count=3)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "['OneCode rocks!', 'OneCode rocks!']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.text_input('my_text', "Nope!")
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_text": "OneCode rocks!"}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "OneCode rocks!"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.text_input('my_text', "Nope", count=4)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_text": ["OneCode", "rocks", "!"]}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "['OneCode', 'rocks', '!']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_optional_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.text_input('my_text', None, optional=True)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "None"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_optional_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.text_input('my_text', 'OneCode rocks!', optional=True)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_text": None}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "None"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_invalid_optional_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.text_input('my_text', None, optional=False)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_text] Value is required: None provided"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_invalid_optional_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.text_input('my_text', 'OneCode rocks!', optional=False)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_text": None}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_text] Value is required: None provided"

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
        x = onecode.text_input('_my_text', None, optional=True)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == 'Key starting with "_" are reserved: _my_text'

    shutil.rmtree(flow_dir)
