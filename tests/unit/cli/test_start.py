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
def test_valid_element_verbose(capsys):
    tmp = tempfile.gettempdir()
    app_file = os.path.join(tmp, 'valid_app.py')
    prepare_streamlit_file(os.path.join('..', '..', 'data', 'flow_1'), app_file, verbose=True)

    captured = capsys.readouterr()

    if os.name == 'nt':
        assert """Processing "Step1"...
 >> (flows\\step1.run) function onecode.csv_reader ✅
 >> (flows\\step1.run) function onecode.dropdown ✅
 >> (flows\\step1.run) function onecode.Logger.info ⏩
 >> (flows\\step1.run) function onecode.Logger.info ⏩
 >> (flows\\step1.run) function <builtin>.range ⏩
 >> (flows\\step1.run) function time.sleep ⏩
 >> (flows\\step1.run) function onecode.Logger.info ⏩
 >> (flows\\step1.run) function onecode.csv_output ✅
 >> (flows\\step1.run) function onecode.Logger.info ⏩
Processing "Step2"...
 >> (flows\\step2.run) function onecode.Project ⏩
 >> (flows\\step2.run) function onecode.Logger.info ⏩
 >> (flows\\step2.run) function onecode.Logger.info ⏩
 >> (flows\\step2.run) function onecode.Logger.info ⏩
 >> (flows\\step2.run) function onecode.Logger.warning ⏩
 >> (flows\\step2.run) function onecode.Logger.error ⏩
 >> (flows\\step2.run) function onecode.Logger.critical ⏩
 >> (flows\\step2.run) function utils.xx ⏩
Processing "Step3"...
 >> (flows\\step3.run) function onecode.slider ✅
 >> (flows\\step3.run) function onecode.Logger.info ⏩
 >> (flows\\step3.run) function onecode.file_input ✅
 >> (flows\\step3.run) function onecode.Logger.info ⏩
 >> (flows\\step3.run) function onecode.file_input ✅
 >> (flows\\step3.run) function onecode.Logger.info ⏩
""" == captured.out
    else:
        assert """Processing "Step1"...
 >> (flows.step1.run) function onecode.csv_reader ✅
 >> (flows.step1.run) function onecode.dropdown ✅
 >> (flows.step1.run) function onecode.Logger.info ⏩
 >> (flows.step1.run) function onecode.Logger.info ⏩
 >> (flows.step1.run) function <builtin>.range ⏩
 >> (flows.step1.run) function time.sleep ⏩
 >> (flows.step1.run) function onecode.Logger.info ⏩
 >> (flows.step1.run) function onecode.csv_output ✅
 >> (flows.step1.run) function onecode.Logger.info ⏩
Processing "Step2"...
 >> (flows.step2.run) function onecode.Project ⏩
 >> (flows.step2.run) function onecode.Logger.info ⏩
 >> (flows.step2.run) function onecode.Logger.info ⏩
 >> (flows.step2.run) function onecode.Logger.info ⏩
 >> (flows.step2.run) function onecode.Logger.warning ⏩
 >> (flows.step2.run) function onecode.Logger.error ⏩
 >> (flows.step2.run) function onecode.Logger.critical ⏩
 >> (flows.step2.run) function flows.utils.xx ⏩
Processing "Step3"...
 >> (flows.step3.run) function onecode.slider ✅
 >> (flows.step3.run) function onecode.Logger.info ⏩
 >> (flows.step3.run) function onecode.file_input ✅
 >> (flows.step3.run) function onecode.Logger.info ⏩
 >> (flows.step3.run) function onecode.file_input ✅
 >> (flows.step3.run) function onecode.Logger.info ⏩
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
