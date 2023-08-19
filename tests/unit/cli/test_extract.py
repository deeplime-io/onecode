import os
import tempfile

from datatest import working_directory

from onecode.cli.extract import extract_json


@working_directory(__file__)
def test_invalid_element(capsys):
    tmp = tempfile.gettempdir()
    json_file = os.path.join(tmp, 'invalid_extraction.json')
    extract_json(os.path.join('..', '..', 'data', 'invalid_flow'), json_file)

    captured = capsys.readouterr()
    assert """Processing Step1...
=> onecode.slider('slider', x, optional=True)
Error  name 'x' is not defined
""" == captured.out

    os.remove(json_file)


@working_directory(__file__)
def test_valid_element_verbose(capsys):
    tmp = tempfile.gettempdir()
    json_file = os.path.join(tmp, 'valid_extraction.json')
    extract_json(os.path.join('..', '..', 'data', 'flow_1'), json_file, verbose=True)

    captured = capsys.readouterr()

    if os.name == 'nt':
        assert """Processing Step1...
 >> (flows\\step1.run) function onecode.csv_reader ✅
 >> (flows\\step1.run) function onecode.dropdown ✅
 >> (flows\\step1.run) function onecode.Logger.info ⏩
 >> (flows\\step1.run) function onecode.Logger.info ⏩
 >> (flows\\step1.run) function <builtin>.range ⏩
 >> (flows\\step1.run) function time.sleep ⏩
 >> (flows\\step1.run) function onecode.Logger.info ⏩
 >> (flows\\step1.run) function onecode.csv_output ✅
 >> (flows\\step1.run) function onecode.Logger.info ⏩
Processing Step2...
 >> (flows\\step2.run) function onecode.Project ⏩
 >> (flows\\step2.run) function onecode.Logger.info ⏩
 >> (flows\\step2.run) function onecode.Logger.info ⏩
 >> (flows\\step2.run) function onecode.Logger.info ⏩
 >> (flows\\step2.run) function onecode.Logger.warning ⏩
 >> (flows\\step2.run) function onecode.Logger.error ⏩
 >> (flows\\step2.run) function onecode.Logger.critical ⏩
 >> (flows\\step2.run) function utils.xx ⏩
Processing Step3...
 >> (flows\\step3.run) function onecode.slider ✅
 >> (flows\\step3.run) function onecode.Logger.info ⏩
 >> (flows\\step3.run) function onecode.file_input ✅
 >> (flows\\step3.run) function onecode.Logger.info ⏩
 >> (flows\\step3.run) function onecode.file_input ✅
 >> (flows\\step3.run) function onecode.Logger.info ⏩
""" == captured.out
    else:
        assert """Processing Step1...
 >> (flows.step1.run) function onecode.csv_reader ✅
 >> (flows.step1.run) function onecode.dropdown ✅
 >> (flows.step1.run) function onecode.Logger.info ⏩
 >> (flows.step1.run) function onecode.Logger.info ⏩
 >> (flows.step1.run) function <builtin>.range ⏩
 >> (flows.step1.run) function time.sleep ⏩
 >> (flows.step1.run) function onecode.Logger.info ⏩
 >> (flows.step1.run) function onecode.csv_output ✅
 >> (flows.step1.run) function onecode.Logger.info ⏩
Processing Step2...
 >> (flows.step2.run) function onecode.Project ⏩
 >> (flows.step2.run) function onecode.Logger.info ⏩
 >> (flows.step2.run) function onecode.Logger.info ⏩
 >> (flows.step2.run) function onecode.Logger.info ⏩
 >> (flows.step2.run) function onecode.Logger.warning ⏩
 >> (flows.step2.run) function onecode.Logger.error ⏩
 >> (flows.step2.run) function onecode.Logger.critical ⏩
 >> (flows.step2.run) function flows.utils.xx ⏩
Processing Step3...
 >> (flows.step3.run) function onecode.slider ✅
 >> (flows.step3.run) function onecode.Logger.info ⏩
 >> (flows.step3.run) function onecode.file_input ✅
 >> (flows.step3.run) function onecode.Logger.info ⏩
 >> (flows.step3.run) function onecode.file_input ✅
 >> (flows.step3.run) function onecode.Logger.info ⏩
""" == captured.out

    os.remove(json_file)
