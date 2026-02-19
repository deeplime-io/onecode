import os

from datatest import working_directory

from onecode import check_modules, get_imported_modules


@working_directory(__file__)
def test_imported_modules():
    modules = get_imported_modules(os.path.join('..', '..', 'data', 'flow_modules'))

    assert set(modules) == {
        'pandas',
        'json',
        'importlib',
        'onecode',
        'os',
        'time',
        'argparse',
        'matplotlib',
    }


@working_directory(__file__)
def test_check_modules():
    project_path = os.path.join('..', '..', 'data', 'flow_modules')
    modules = check_modules(
        modules=get_imported_modules(project_path),
        requirements_file=os.path.join(project_path, 'requirements.txt')
    )

    assert set(modules.keys()) == {
        'pandas',
        'json',
        'importlib',
        'onecode',
        'os',
        'time',
        'argparse',
        'matplotlib'
    }

    assert modules['argparse'] == {
        'in_env': True,
        'builtin': True,
        'version': None,
        'dist_name': 'argparse',
        'msg': None
    }
    assert modules['importlib'] == {
        'in_env': True,
        'builtin': True,
        'version': None,
        'dist_name': 'importlib',
        'msg': None
    }
    assert modules['json'] == {
        'in_env': True,
        'builtin': True,
        'version': None,
        'dist_name': 'json',
        'msg': None
    }
    assert modules['os'] == {
        'in_env': True,
        'builtin': True,
        'version': None,
        'dist_name': 'os',
        'msg': None
    }
    assert modules['time'] == {
        'in_env': True,
        'builtin': True,
        'version': None,
        'dist_name': 'time',
        'msg': None
    }

    assert modules['onecode']['version'].split('.dev')[0] == "1.2.1"
    assert modules['onecode']['in_env'] is True
    assert modules['onecode']['builtin'] is False
    assert modules['onecode']['dist_name'] == 'onecode'
    assert modules['onecode']['msg'] == (
        f"⚠️ onecode version mismatch: {modules['onecode']['version']} vs"
        f" <1 in requirements.txt"
    )

    assert modules['pandas']['in_env'] is True
    assert modules['pandas']['builtin'] is False
    assert modules['pandas']['dist_name'] == 'pandas'
    assert modules['pandas']['msg'] == '🚫 pandas not in requirements.txt'

    assert modules['matplotlib']['in_env'] is False
    assert modules['matplotlib']['builtin'] is False
    assert modules['matplotlib']['dist_name'] == 'matplotlib'
    assert modules['matplotlib']['msg'] == '💥 matplotlib not in Python environment'
