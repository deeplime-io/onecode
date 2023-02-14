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
def test_execute_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    _generate_csv_file(flow_dir, 'test.csv')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    import os
    import pandas as pd

    x = onecode.csv_reader('my_csv_reader', 'test.csv')
    with open("stdout.txt", 'w') as f:
        df = pd.read_csv(os.path.join(onecode.Project().data_root, 'test.csv'))
        f.write(str(df.equals(x)))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "True"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    _generate_csv_file(flow_dir, 'test.csv')

    # count is ignored at loading & execution as it is only used by streamlit
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    import os
    import pandas as pd

    x = onecode.csv_reader('my_csv_reader', ['test.csv', 'test.csv'], count=3)
    with open("stdout.txt", 'w') as f:
        df = pd.read_csv(os.path.join(onecode.Project().data_root, 'test.csv'))
        f.write(str([df.equals(x_df) for x_df in x]))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[True, True]"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    _generate_csv_file(flow_dir, 'test.csv')

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    import os
    import pandas as pd

    x = onecode.csv_reader('my_csv_reader', 'test.csv')
    with open("stdout.txt", 'w') as f:
        df = pd.read_csv(os.path.join(onecode.Project().data_root, 'test.csv'))
        f.write(str(df.equals(x)))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_csv_reader": "test.csv"}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "True"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_multiple_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    _generate_csv_file(flow_dir, 'test.csv')

    # count is ignored at loading & execution as it is only used by streamlit
    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    import os
    import pandas as pd

    x = onecode.csv_reader('my_csv_reader', 'test.csv', count=4)
    with open("stdout.txt", 'w') as f:
        df = pd.read_csv(os.path.join(onecode.Project().data_root, 'test.csv'))
        f.write(str([df.equals(x_df) for x_df in x]))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_csv_reader": ["test.csv", "test.csv", "test.csv"]}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[True, True, True]"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_invalid_csv():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    with open(os.path.join(flow_dir, 'data', 'test.csv'), 'w') as f:
        f.write("A,B,C\n")

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    import os
    import pandas as pd

    try:
        x = onecode.csv_reader('my_csv_reader', 'test.csv')
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_csv_reader] Empty dataframe"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_load_then_execute_invalid_csv():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)
    _generate_csv_file(flow_dir, 'valid.csv')
    with open(os.path.join(flow_dir, 'data', 'test.csv'), 'w') as f:
        f.write("A,B,C\n")

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    import os
    import pandas as pd

    try:
        x = onecode.csv_reader('my_csv_reader', 'valid.csv')
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_csv_reader": "test.csv"}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_csv_reader] Empty dataframe"

    shutil.rmtree(flow_dir)


@pytest.mark.emulations
def test_execute_optional_value():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'a') as f:
        f.write("""
    x = onecode.csv_reader('my_csv_reader', None, optional=True)
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
    x = onecode.csv_reader('my_csv_reader', 'test.csv', optional=True)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_csv_reader": None}, f)

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
        x = onecode.slider('my_csv_reader', None, optional=False)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_csv_reader] Value is required: None provided"

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
        x = onecode.csv_reader('my_csv_reader', 'test.csv', optional=False)
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    params = os.path.join(flow_dir, 'params.json')
    with open(params, 'w') as f:
        json.dump({"my_csv_reader": None}, f)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py {params}')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == "[my_csv_reader] Value is required: None provided"

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
        x = onecode.csv_reader('_my_csv_reader', 'test.csv')
    except ValueError as err:
        with open("stdout.txt", 'w') as f:
            f.write(str(err))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == 'Key starting with "_" are reserved: _my_csv_reader'

    shutil.rmtree(flow_dir)
