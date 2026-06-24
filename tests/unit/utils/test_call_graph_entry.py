import os

import pytest
from datatest import working_directory

from onecode import get_call_graph_entry_files


@working_directory(__file__)
def test_get_call_graph_entry_files_flow_1():
    project_path = os.path.join('..', '..', 'data', 'flow_1')
    entry_files = get_call_graph_entry_files(project_path)

    assert entry_files[0].endswith('main.py')
    assert set(os.path.basename(f) for f in entry_files[1:]) == {
        'step1.py', 'step2.py', 'step3.py', 'utils.py'
    }
    assert 'unused.py' not in {os.path.basename(f) for f in entry_files}


@working_directory(__file__)
def test_get_call_graph_entry_files_flow_modules():
    project_path = os.path.join('..', '..', 'data', 'flow_modules')
    entry_files = get_call_graph_entry_files(project_path)

    assert entry_files == [
        os.path.abspath(os.path.join(project_path, 'main.py')),
        os.path.abspath(os.path.join(project_path, 'flows', 'flow_modules.py')),
    ]


def test_get_call_graph_entry_files_missing_main(tmp_path):
    with pytest.raises(FileNotFoundError, match='main.py not found'):
        get_call_graph_entry_files(str(tmp_path))


def test_get_call_graph_entry_files_missing_config(tmp_path):
    (tmp_path / 'main.py').write_text('print("hello")\n')

    with pytest.raises(FileNotFoundError, match='Ensure you are at the root'):
        get_call_graph_entry_files(str(tmp_path))
