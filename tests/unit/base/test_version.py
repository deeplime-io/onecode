import toml
from datatest import working_directory

import onecode


@working_directory(__file__)
def test_version():
    with open('../../../pyproject.toml', 'r') as f:
        parsed_toml = toml.load(f)
        assert onecode.__version__ == parsed_toml['tool']['poetry']['version']
