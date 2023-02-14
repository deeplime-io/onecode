from datatest import working_directory

from tests.utils.format import strip


@working_directory(__file__)
def test_skeleton_multiple_flows_1():
    with open('../../../onecode/cli/skeleton/main.py', 'r') as out_file:
        out = strip(out_file.read())

    with open('../../data/flow_1/main.py', 'r') as truth_file:
        truth = strip(truth_file.read())

    assert out == truth
