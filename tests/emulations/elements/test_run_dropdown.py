import json
import os
import shutil

import pytest

from onecode import Env
from onecode.cli.create import create
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


@pytest.mark.emulations
def test_execute_single_value_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.dropdown('my_dropdown', 'B', options=['A', 'B', 'C'])
    with open("stdout.txt", 'w') as f:
        f.write(x)
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "B"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_multiple_values_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.dropdown('my_dropdown', ['B', 'C'], options=['A', 'B', 'C'], multiple=True)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "['B', 'C']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_single_value_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.dropdown('my_dropdown', ['B', 'B'], options=['A', 'B', 'C'], count=3)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "['B', 'B']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_multiple_values_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.dropdown(
        'my_dropdown',
        [['B', 'C']],
        options=['A', 'B', 'C'],
        multiple=True,
        count=3
    )
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[['B', 'C']]"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_single_value_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.dropdown('my_dropdown', 'B', options=['A', 'B', 'C'])
    with open("stdout.txt", 'w') as f:
        f.write(x)
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_dropdown": "B"}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "B"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_multiple_values_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.dropdown('my_dropdown', ['B', 'C'], options=['A', 'B', 'C'], multiple=True)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_dropdown": ["B", "C"]}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "['B', 'C']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_single_value_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.dropdown('my_dropdown', ['B', 'B', 'B'], options=['A', 'B', 'C'], count=4)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_dropdown": ["B", "B"]}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "['B', 'B']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_multiple_values_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.dropdown(
        'my_dropdown',
        ['B', 'C'],
        options=['A', 'B', 'C'],
        multiple=True,
        count=4
    )
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_dropdown": [["B", "C"], ["B", "C"], ["B", "C"]]}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[['B', 'C'], ['B', 'C'], ['B', 'C']]"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_invalid_single_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.dropdown('my_dropdown', 'D', options=['A', 'B', 'C'])
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_dropdown] Not a valid choice: D"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_invalid_single_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.dropdown('my_dropdown', 'B', options=['A', 'B', 'C'])
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_dropdown": "D"}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_dropdown] Not a valid choice: D"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_invalid_multiple_values():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.dropdown('my_dropdown', ['B', 'C', 'D'], options=['A', 'B', 'C'], multiple=True)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_dropdown] Not a valid choice: D"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_invalid_multiple_values():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.dropdown('my_dropdown', ['B', 'C'], options=['A', 'B', 'C'], multiple=True)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_dropdown": ["B", "C", "D"]}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_dropdown] Not a valid choice: D"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_invalid_multiple_values_with_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.dropdown(
            'my_dropdown',
            ['B', 'C'],
            options=['A', 'B', 'C'],
            multiple=True,
            count=4
        )
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_dropdown": [["B", "C"], ["B", "C"], ["B", "C", "D"]]}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_dropdown] Not a valid choice: D"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_optional_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.dropdown('my_dropdown', None, options=['A', 'B', 'C'], optional=True)
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
    x = onecode.dropdown('my_dropdown', 'B', options=['A', 'B', 'C'], optional=True)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_dropdown": None}, f)

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
        x = onecode.dropdown('my_dropdown', None, options=['A', 'B', 'C'], optional=False)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_dropdown] Value is required: None provided"

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
        x = onecode.dropdown('my_dropdown', 'B', options=['A', 'B', 'C'], optional=False)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_dropdown": None}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_dropdown] Value is required: None provided"

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
        x = onecode.dropdown('_my_dropdown', 'B', options=['A', 'B', 'C'])
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == 'Key starting with "_" are reserved: _my_dropdown'

    shutil.rmtree(flow_dir)
