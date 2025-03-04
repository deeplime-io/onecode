import os
import tempfile

from datatest import working_directory

from onecode import write_requirements


@working_directory(__file__)
def test_write_requirements():
    tmp = tempfile.gettempdir()
    req_file = os.path.join(tmp, 'requirements.txt')

    write_requirements(
        req_file,
        os.path.join('..', '..', 'data', 'flow_modules'),
        specify_version=False
    )

    with open(req_file) as f:
        modules = f.readlines()

    os.remove(req_file)
    assert set(modules) == {
        'matplotlib\n',
        'onecode\n',
        'pandas\n'
    }
