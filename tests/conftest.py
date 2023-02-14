import os

import pytest

from onecode import Env, Logger, Mode, Project


@pytest.fixture(autouse=True)
def clear_project():
    if Env.ONECODE_PROJECT_DATA in os.environ:
        del os.environ[Env.ONECODE_PROJECT_DATA]
    Project().reset()
    Logger().reset()
    Project().mode = Mode.EXECUTE


def pytest_addoption(parser):
    parser.addoption(
        "--with-emulations", action="store_true", default=False, help="run emulations tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "emulations: mark test as emulations needed to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--with-emulations"):
        return

    skip_emulation = pytest.mark.skip(reason="need --with-emulations option to run")
    for item in items:
        if "emulations" in item.keywords:
            item.add_marker(skip_emulation)
