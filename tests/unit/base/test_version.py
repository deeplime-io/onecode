import tomllib

from datatest import working_directory

import onecode


@working_directory(__file__)
def test_version():
    with open('../../../pyproject.toml', 'rb') as f:
        parsed_toml = tomllib.load(f)
        assert onecode.__version__ == parsed_toml['tool']['poetry']['version']
