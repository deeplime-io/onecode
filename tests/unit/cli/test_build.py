import json
import os
import tempfile

from datatest import working_directory

from onecode.cli.build import extract_gui


@working_directory(__file__)
def test_invalid_build(capsys):
    tmp = tempfile.gettempdir()
    json_file = os.path.join(tmp, 'invalid_extraction.json')
    extract_gui(os.path.join('..', '..', 'data', 'invalid_flow'), json_file, verbose=False)

    captured = capsys.readouterr()
    assert """Processing Step1...
=> onecode.slider('slider', x, optional=True)
Error  name 'x' is not defined
""" == captured.out

    os.remove(json_file)


@working_directory(__file__)
def test_valid_build_verbose(capsys):
    tmp = tempfile.gettempdir()
    json_file = os.path.join(tmp, 'valid_app_ui.json')
    extract_gui(os.path.join('..', '..', 'data', 'flow_1'), json_file, verbose=False)

    captured = capsys.readouterr()

    assert captured.out == """Processing Step1...
Processing Step2...
Processing Step3...
"""

    # as app_ui.json uses set() for dependencies,
    # it is not possible to predict the order of the list
    with open(os.path.join('..', '..', 'data', 'flow_1', 'ground_truth_app_ui_order1.json')) as f:
        gt_1 = json.load(f)

    with open(os.path.join('..', '..', 'data', 'flow_1', 'ground_truth_app_ui_order2.json')) as f:
        gt_2 = json.load(f)

    with open(json_file) as f:
        app_ui = json.load(f)

    assert gt_1 == app_ui or gt_2 == app_ui

    os.remove(json_file)
