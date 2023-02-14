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
    assert """Processing "Step1"...
=> onecode.slider('slider', x, optional=True)
Error  name 'x' is not defined
""" == captured.out

    os.remove(json_file)
