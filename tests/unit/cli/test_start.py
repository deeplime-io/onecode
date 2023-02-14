import os
import tempfile

from datatest import working_directory

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
