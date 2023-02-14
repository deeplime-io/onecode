import os

import pytest
from datatest import working_directory

from onecode import Project, process_call_graph, register_ext_module


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
