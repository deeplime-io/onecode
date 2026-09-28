import logging
import os

import pytest

from onecode import Env, Logger, Mode, Project


@pytest.fixture(autouse=True)
def clear_project():
    if Env.ONECODE_PROJECT_DATA in os.environ:
        del os.environ[Env.ONECODE_PROJECT_DATA]
    Project().reset()
    Logger().reset()
    logger = logging.getLogger(Env.ONECODE_LOGGER_NAME)
    logger.propagate = True
    Project().mode = Mode.EXECUTE
