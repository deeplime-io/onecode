import json
import os
import shutil

import pytest

from onecode import Env
from onecode.cli.create import create
from tests.utils.flow_cli import (
    _clean_flow,
    _generate_csv_file,
    _generate_flow_name
)


@pytest.mark.emulations
def test_execute_single_value_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file.txt')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.file_input('my_file_input', 'input/test_file.txt')
    with open("stdout.txt", 'w') as f:
        f.write(x)
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"{flow_data}/input/test_file.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_multiple_values_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file_1.txt')
    _generate_csv_file(flow_dir, 'input/test_file_2.txt')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.file_input(
        'my_file_input',
        ['input/test_file_1.txt', 'input/test_file_2.txt'],
        multiple=True
    )
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"['{flow_data}/input/test_file_1.txt'," \
                           f" '{flow_data}/input/test_file_2.txt']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_single_value_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file.txt')

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.file_input('my_file_input', ['input/test_file.txt', 'input/test_file.txt'], count=3)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"['{flow_data}/input/test_file.txt'," \
                           f" '{flow_data}/input/test_file.txt']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_multiple_values_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file_1.txt')
    _generate_csv_file(flow_dir, 'input/test_file_2.txt')

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.file_input(
        'my_file_input',
        [['input/test_file_1.txt', 'input/test_file_2.txt']],
        multiple=True,
        count=3
    )
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == \
            f"[['{flow_data}/input/test_file_1.txt', '{flow_data}/input/test_file_2.txt']]"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_single_value_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file.txt')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.file_input('my_file_input', 'input/test_file.txt')
    with open("stdout.txt", 'w') as f:
        f.write(x)
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_file_input": "input/test_file.txt"}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"{flow_data}/input/test_file.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_multiple_values_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file_1.txt')
    _generate_csv_file(flow_dir, 'input/test_file_2.txt')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.file_input(
        'my_file_input',
        ['input/test_file_1.txt', 'input/test_file_2.txt'],
        multiple=True
    )
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_file_input": ['input/test_file_1.txt', 'input/test_file_2.txt']}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"['{flow_data}/input/test_file_1.txt'," \
                           f" '{flow_data}/input/test_file_2.txt']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_single_value_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file.txt')

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.file_input('my_file_input', 'input/test_file.txt', count=4)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({
            "my_file_input": ["input/test_file.txt", "input/test_file.txt", "input/test_file.txt"]
        }, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"['{flow_data}/input/test_file.txt'," \
                           f" '{flow_data}/input/test_file.txt'," \
                           f" '{flow_data}/input/test_file.txt']"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_multiple_values_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file_1.txt')
    _generate_csv_file(flow_dir, 'input/test_file_2.txt')

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.file_input(
        'my_file_input',
        ['input/test_file_1.txt', 'input/test_file_2.txt'],
        multiple=True,
        count=3
    )
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({
                "my_file_input": [
                    ['input/test_file_1.txt', 'input/test_file_2.txt'],
                    ['input/test_file_1.txt', 'input/test_file_2.txt']
                ]
            },
            f
        )

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == \
            f"[['{flow_data}/input/test_file_1.txt', '{flow_data}/input/test_file_2.txt']," \
            f" ['{flow_data}/input/test_file_1.txt', '{flow_data}/input/test_file_2.txt']]"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_file_not_found_single_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.file_input('my_file_input', 'input/test_file.txt')
    except FileNotFoundError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"[my_file_input] File not found: {flow_data}/input/test_file.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_execute_file_not_found_single_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file.txt')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.file_input('my_file_input', 'input/test_file.txt')
    except FileNotFoundError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_file_input": "input/test_file_1.txt"}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"[my_file_input] File not found: {flow_data}/input/test_file_1.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_not_a_file_single_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    os.makedirs(os.path.join(flow_data, 'input', 'test_file.txt'))

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.file_input('my_file_input', 'input/test_file.txt')
    except FileNotFoundError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"[my_file_input] Path is not a file: {flow_data}/input/test_file.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_execute_not_a_file_single_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file.txt')
    os.makedirs(os.path.join(flow_data, 'input', 'test_file_1.txt'))

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.file_input('my_file_input', 'input/test_file.txt')
    except FileNotFoundError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_file_input": "input/test_file_1.txt"}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"[my_file_input] Path is not a file: {flow_data}/input/test_file_1.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_file_not_found_multiple_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file_1.txt')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.file_input(
            'my_file_input',
            ['input/test_file_1.txt', 'input/test_file_2.txt'],
            multiple=True
        )
    except FileNotFoundError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"[my_file_input] File not found: {flow_data}/input/test_file_2.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_execute_file_not_found_multiple_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file_1.txt')
    _generate_csv_file(flow_dir, 'input/test_file_2.txt')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.file_input(
            'my_file_input',
            ['input/test_file_1.txt', 'input/test_file_2.txt'],
            multiple=True
        )
    except FileNotFoundError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_file_input": ['input/test_file_1.txt', 'input/test_file_3.txt']}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"[my_file_input] File not found: {flow_data}/input/test_file_3.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_not_a_file_multiple_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file_1.txt')
    _generate_csv_file(flow_dir, 'input/test_file_2.txt')
    os.makedirs(os.path.join(flow_data, 'input', 'test_file.txt'))

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.file_input(
            'my_file_input',
            ['input/test_file_1.txt', 'input/test_file.txt'],
            multiple=True
        )
    except FileNotFoundError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"[my_file_input] Path is not a file: {flow_data}/input/test_file.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_execute_not_a_file_multiple_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file.txt')
    os.makedirs(os.path.join(flow_data, 'input', 'test_file_1.txt'))

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.file_input(
            'my_file_input',
            ['input/test_file.txt'],
            multiple=True
        )
    except FileNotFoundError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_file_input": ['input/test_file.txt', 'input/test_file_1.txt']}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"[my_file_input] Path is not a file: {flow_data}/input/test_file_1.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_execute_not_a_file_multiple_value_with_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    flow_data = os.path.join(flow_dir, 'data')
    _generate_csv_file(flow_dir, 'input/test_file_1.txt')
    os.makedirs(os.path.join(flow_data, 'input', 'test_file.txt'))

    # count is ignored at loading & execution as it is only used in UI mode
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    try:
        x = onecode.file_input(
            'my_file_input',
            ['input/test_file_1.txt'],
            multiple=True,
            count=3
        )
    except FileNotFoundError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({
            "my_file_input": [
                ['input/test_file_1.txt'],
                ['input/test_file_1.txt'],
                ['input/test_file_1.txt', 'input/test_file.txt'],
            ]},
            f
        )
    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"[my_file_input] Path is not a file: {flow_data}/input/test_file.txt"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_optional_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.file_input('my_file_input', None, optional=True)
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
    x = onecode.file_input('my_file_input', 'input/test_file.txt', optional=True)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_file_input": None}, f)

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
        x = onecode.file_input('my_file_input', None, optional=False)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_file_input] Value is required: None provided"

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
        x = onecode.file_input('my_file_input', 'input/test_file.txt', optional=False)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_file_input": None}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_file_input] Value is required: None provided"

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
        x = onecode.file_input('_my_file_input', 'input/test_file.txt')
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == 'Key starting with "_" are reserved: _my_file_input'

    shutil.rmtree(flow_dir)
