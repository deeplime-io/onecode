import os
import tempfile

from datatest import working_directory

from onecode.cli.extract import extract_json
from tests.utils.format import strip


@working_directory(__file__)
def test_multiple_flows_extraction_1():
    tmp = tempfile.gettempdir()
    parameter_file = os.path.join(tmp, 'extracted.json')

    extract_json('../../data/flow_1', parameter_file)

    with open(parameter_file, 'r') as out_file:
        out = strip(out_file.read())

    with open('../../data/flow_1/ground_truth.json', 'r') as truth_file:
        truth = strip(truth_file.read())

    assert out == truth
    os.remove(parameter_file)


@working_directory(__file__)
def test_multiple_flows_extraction_all_1():
    tmp = tempfile.gettempdir()
    parameter_file = os.path.join(tmp, 'extracted_all.json')

    extract_json('../../data/flow_1', parameter_file, all=True)

    with open(parameter_file, 'r') as out_file:
        out = strip(out_file.read())

    with open('../../data/flow_1/ground_truth_all.json', 'r') as truth_file:
        truth = strip(truth_file.read())

    assert out == truth
    os.remove(parameter_file)
