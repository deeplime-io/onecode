import os

import pytest
from datatest import working_directory

from onecode import Project, register_ext_module
from onecode.cli import process_call_graph
from onecode.cli.utils import _resolve_graph_key, extract_calls


def test_resolve_graph_key_windows_style():
    graph = {
        'flows\\step1.run': [],
        'flows\\step2.run': [
            {
                'normed': 'utils.xx',
                'code': 'xx()',
            }
        ],
        'flows\\utils.xx': [
            {
                'normed': 'onecode.slider',
                'code': "onecode.slider('My slider\"1', 0.5, max=6)",
            }
        ],
    }

    assert _resolve_graph_key('flows.step1.run', graph) == 'flows\\step1.run'
    assert _resolve_graph_key('utils.xx', graph) == 'flows\\utils.xx'


def test_extract_calls_resolves_windows_helper_modules():
    graph = {
        'flows\\step2.run': [
            {
                'normed': 'utils.xx',
                'code': 'xx()',
            }
        ],
        'flows\\utils.xx': [
            {
                'normed': 'onecode.slider',
                'code': "onecode.slider('My slider\"1', 0.5, max=6)",
            }
        ],
    }

    Project().reset()
    calls = []
    extract_calls('flows.step2.run', graph, calls)

    assert len(calls) == 1
    assert calls[0]['func'] == 'onecode.slider'


def test_invalid_call_graph():
    with pytest.raises(FileNotFoundError) as excinfo:
        process_call_graph()

    assert "Ensure you are at the root of your OneCode project" == str(excinfo.value)


@working_directory(__file__)
def test_register_ext_module():
    register_ext_module(os.path.join('..', '..', 'data', 'flow_1'))

    assert 'onecode_ext.EmptyInput' in Project().registered_elements

    Project().reset()
    assert 'onecode_ext.EmptyInput' not in Project().registered_elements
