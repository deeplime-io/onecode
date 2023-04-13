import os
import tempfile

from datatest import working_directory

from onecode import register_ext_module
from onecode.cli.start import prepare_streamlit_file


@working_directory(__file__)
def test_invalid_element(capsys):
    tmp = tempfile.gettempdir()
    app_file = os.path.join(tmp, 'invalid_app.py')
    prepare_streamlit_file(os.path.join('..', '..', 'data', 'invalid_flow'), app_file)

    captured = capsys.readouterr()
    assert """Processing "Step1"...
=> onecode.slider('slider', x, optional=True)
Error  name 'x' is not defined
""" == captured.out

    os.remove(app_file)


@working_directory(__file__)
def test_invalid_import(capsys):
    tmp = tempfile.gettempdir()
    app_file = os.path.join(tmp, 'invalid_app.py')
    project_path = os.path.join('..', '..', 'data', 'invalid_element')

    register_ext_module(project_path, "ext")
    prepare_streamlit_file(project_path, app_file)

    captured = capsys.readouterr()
    assert """Processing "Step1"...
=> ext.invalid_elem_imports
=> ext.invalid_elem_init
Error  name 'ext' is not defined
=> ext.invalid_elem('test', 0.5)
Error  name 'ext' is not defined
""" == captured.out

    os.remove(app_file)
