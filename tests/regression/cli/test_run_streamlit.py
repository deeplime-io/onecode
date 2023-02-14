import os
import tempfile

from datatest import working_directory

from onecode import Env, Project
from onecode.cli.start import prepare_streamlit_file
from tests.utils.format import strip


@working_directory(__file__)
def test_multiple_flows_streamlit_1():
    tmp = tempfile.gettempdir()
    app_file = os.path.join(tmp, 'extracted_app.py')

    # # pytest only has one session, i-e one Project() for all tests
    # # necessary to reset the original data path
    os.environ[Env.ONECODE_PROJECT_DATA] = '../../data/flow_1/data'
    Project().reset()
    prepare_streamlit_file('../../data/flow_1', app_file)
    del os.environ[Env.ONECODE_PROJECT_DATA]

    with open(app_file, 'r') as out_file:
        out = strip(out_file.read())

    with open('../../data/flow_1/app.py', 'r') as truth_file:
        truth = strip(truth_file.read())

    # OS diff due to backslash vs forward slash
    if os.name == 'nt':
        assert out == truth.replace('/README.md', '\\README.md')
    else:
        assert out == truth

    os.remove(app_file)
