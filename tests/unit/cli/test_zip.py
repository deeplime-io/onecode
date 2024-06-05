import os
import shutil

from datatest import working_directory

from onecode import Env, FileOutput, Mode, Project
from onecode.cli.create import create
from onecode.cli.zip import zip_output
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


@working_directory(__file__)
def test_zip_verbose(capsys):
    _, folder, flow_id = _generate_flow_name()
    tmp = _clean_flow(folder)

    folder_path = os.path.join(tmp, folder)
    data_path = os.path.join(folder_path, 'data')

    create(tmp, folder, cli=False)

    os.environ[Env.ONECODE_PROJECT_DATA] = data_path
    Project().reset()
    Project().mode = Mode.EXECUTE
    Project().current_flow = flow_id

    test1_out = FileOutput(
        key="test1",
        value="test1.txt"
    )

    test2_out = FileOutput(
        key="test2",
        value="test2.txt"
    )

    test1 = test1_out()
    with open(test1, 'w') as f:
        f.write('Test1')

    test2 = test2_out()
    with open(test2, 'w') as f:
        f.write('Test2')

    zip_output(
        folder_path,
        data_path,
        os.path.join(folder_path, 'data.zip'),
        compression_level=0,
        verbose=True
    )

    captured = capsys.readouterr()
    logs = captured.out.split('\n')[-4:]
    print(logs)

    # keep only the logs from zip, not from create
    assert '\n'.join(logs) == f"""Processing flow {folder}...
Archiving test1: {test1} => {os.path.join('outputs', 'test1.txt')}
Archiving test2: {test2} => {os.path.join('outputs', 'test2.txt')}
"""

    try:
        shutil.rmtree(folder_path)
    except Exception:
        pass
