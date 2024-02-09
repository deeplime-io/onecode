import json
import os
import shutil
import sys

import pytest

from onecode import ConfigOption, Env, Mode, Project
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


def test_empty_project():
    p = Project()

    assert p.registered_elements == {
        'onecode.Checkbox',
        'onecode.CsvReader',
        'onecode.Dropdown',
        'onecode.FileInput',
        'onecode.FolderInput',
        'onecode.NumberInput',
        'onecode.RadioButton',
        'onecode.Slider',
        'onecode.TextInput',
        'onecode.FileOutput',
        'onecode.CsvOutput',
        'onecode.ImageOutput',
        'onecode.PlotlyOutput',
        'onecode.PyvistaVrmlOutput',
        'onecode.TextOutput',
        'onecode.VideoOutput',
        'onecode.HtmlOutput',
        'onecode.SectionHeader'
    }
    assert p.mode == Mode.EXECUTE
    assert p.current_flow is None
    assert p.data is None
    assert p.config == {
        ConfigOption.FLUSH_STDOUT: False,
        ConfigOption.LOGGER_COLOR: True,
        ConfigOption.LOGGER_TIMESTAMP: True,
    }
    assert p.data_root == os.getcwd()
    assert p.get_input_path('test.txt') == os.path.join(os.getcwd(), 'test.txt')
    assert p.get_input_path('/path/to/test.txt') == '/path/to/test.txt'
    assert p.get_output_path('test.txt') == os.path.join(os.getcwd(), 'outputs', 'test.txt')
    assert p.get_output_path('/path/to/test.txt') == '/path/to/test.txt'


def test_project_reset():
    p = Project()
    data_path = os.path.join(os.getcwd(), 'tests', 'data')
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    p.reset()

    p.register_element('NewLib.NewElement')
    p.mode = Mode.STREAMLIT
    p.data = {"x": 4}
    p.current_flow = 'testflow'
    p.set_config(ConfigOption.FLUSH_STDOUT, True)

    assert p.registered_elements == {
        'onecode.Checkbox',
        'onecode.CsvReader',
        'onecode.Dropdown',
        'onecode.FileInput',
        'onecode.FolderInput',
        'onecode.NumberInput',
        'onecode.RadioButton',
        'onecode.Slider',
        'onecode.TextInput',
        'onecode.FileOutput',
        'onecode.CsvOutput',
        'onecode.ImageOutput',
        'onecode.PlotlyOutput',
        'onecode.PyvistaVrmlOutput',
        'onecode.TextOutput',
        'onecode.VideoOutput',
        'onecode.HtmlOutput',
        'onecode.SectionHeader',
        'NewLib.NewElement'
    }
    assert p.mode == Mode.STREAMLIT
    assert p.current_flow == 'testflow'
    assert p.data == {"x": 4}
    assert p.config == {
        ConfigOption.FLUSH_STDOUT: True,
        ConfigOption.LOGGER_COLOR: True,
        ConfigOption.LOGGER_TIMESTAMP: True,
    }
    assert p.data_root == data_path
    assert p.get_input_path('test.txt') == os.path.join(data_path, 'test.txt')
    assert p.get_input_path('/path/to/test.txt') == '/path/to/test.txt'
    assert p.get_output_path('test.txt') == os.path.join(data_path, 'outputs', 'test.txt')
    assert p.get_output_path('/path/to/test.txt') == '/path/to/test.txt'

    del os.environ[Env.ONECODE_PROJECT_DATA]
    p.reset()
    assert p.registered_elements == {
        'onecode.Checkbox',
        'onecode.CsvReader',
        'onecode.Dropdown',
        'onecode.FileInput',
        'onecode.FolderInput',
        'onecode.NumberInput',
        'onecode.RadioButton',
        'onecode.Slider',
        'onecode.TextInput',
        'onecode.FileOutput',
        'onecode.CsvOutput',
        'onecode.ImageOutput',
        'onecode.PlotlyOutput',
        'onecode.PyvistaVrmlOutput',
        'onecode.TextOutput',
        'onecode.VideoOutput',
        'onecode.HtmlOutput',
        'onecode.SectionHeader'
    }
    assert p.mode == Mode.CONSOLE
    assert p.current_flow is None
    assert p.data is None
    assert p.config == {
        ConfigOption.FLUSH_STDOUT: False,
        ConfigOption.LOGGER_COLOR: True,
        ConfigOption.LOGGER_TIMESTAMP: True
    }
    assert p.data_root == os.getcwd()
    assert p.get_input_path('test.txt') == os.path.join(os.getcwd(), 'test.txt')
    assert p.get_input_path('/path/to/test.txt') == '/path/to/test.txt'
    assert p.get_output_path('test.txt') == os.path.join(os.getcwd(), 'outputs', 'test.txt')
    assert p.get_output_path('/path/to/test.txt') == '/path/to/test.txt'


def test_output_manifest():
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)
    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')

    os.makedirs(data_path)
    os.environ[Env.ONECODE_PROJECT_DATA] = data_path

    Project().reset()
    p = Project()
    p.current_flow = flow_id

    assert p.current_flow == flow_id
    assert p.get_output_manifest() == os.path.join(data_path, 'outputs', flow_id, 'MANIFEST.txt')

    d = {"name": "test"}
    p.write_output(d)
    with open(p.get_output_manifest()) as f:
        assert json.load(f) == d

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass


def test_set_mode():
    p = Project()

    for m in enumerate(Mode):
        p.mode = m
        assert p.mode == m


def test_project_data():
    p = Project()
    p.add_data('x', 5)

    assert p.data['x'] == 5

    with pytest.raises(ValueError) as excinfo:
        p.add_data('', 3)

    assert "Key cannot be null" == str(excinfo.value)


def test_project_cwd_data_path():
    data_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'data')
    os.makedirs(data_path)

    p = Project()
    p.reset()
    data_root = p.data_root

    try:
        shutil.rmtree(data_path)
    except Exception:
        pass

    assert data_root == data_path


def test_project_invalid_register_element():
    p = Project()

    with pytest.raises(ValueError) as excinfo:
        p.register_element('NewLib.NewElement.X')

    assert 'Invalid element name: NewLib.NewElement.X must be of form "<module>.<class_name>"' == \
        str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        p.register_element('NewLib')

    assert 'Invalid element name: NewLib must be of form "<module>.<class_name>"' == \
        str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        p.register_element('NewLib.new_element')

    assert 'Invalid element name: new_element must not be snake case' == \
        str(excinfo.value)


def test_invalid_data_path():
    p = Project()

    with pytest.raises(NotADirectoryError) as excinfo:
        p._set_data_root('fake')

    assert 'Invalid data path: fake' == str(excinfo.value)


def test_config_option():
    p = Project()

    p.set_config('XX', 56.4)
    assert p.get_config('XX') == 56.4
    assert p.config == {
        ConfigOption.FLUSH_STDOUT: False,
        ConfigOption.LOGGER_COLOR: True,
        ConfigOption.LOGGER_TIMESTAMP: True,
        'XX': 56.4
    }


def test_invalid_config_option():
    p = Project()

    with pytest.raises(KeyError) as excinfo:
        p.get_config('XX')

    assert "'XX'" == str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        p.set_config('', True)

    assert "Key cannot be null" == str(excinfo.value)
