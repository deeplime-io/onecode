import logging

from onecode import ColoredFormatter, ConfigOption, Logger, Project


def test_logger_debug(caplog):
    Logger().set_level(logging.DEBUG)
    with caplog.at_level(logging.DEBUG):
        Logger.debug("This is a debug")

    assert logging.DEBUG == caplog.record_tuples[0][1]
    assert "This is a debug" == caplog.record_tuples[0][2]


def test_logger_info(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info("This is an info")
        Logger.warning("This is a warning")

    assert logging.INFO == caplog.record_tuples[0][1]
    assert "This is an info" == caplog.record_tuples[0][2]

    assert logging.WARNING == caplog.record_tuples[1][1]
    assert "This is a warning" == caplog.record_tuples[1][2]


def test_logger_warning(caplog):
    with caplog.at_level(logging.WARNING):
        Logger.warning("This is a warning")
        Logger.info("This is an info")

    assert logging.WARNING == caplog.record_tuples[0][1]
    assert "This is a warning" == caplog.record_tuples[0][2]
    assert len(caplog.record_tuples) == 1


def test_logger_error(caplog):
    with caplog.at_level(logging.ERROR):
        Logger.error("This is an error")
        Logger.warning("This is a warning")

    assert logging.ERROR == caplog.record_tuples[0][1]
    assert "This is an error" == caplog.record_tuples[0][2]
    assert len(caplog.record_tuples) == 1


def test_logger_critical(caplog):
    with caplog.at_level(logging.CRITICAL):
        Logger.critical("This is a critical error")
        Logger.error("This is an error")

    assert logging.CRITICAL == caplog.record_tuples[0][1]
    assert "This is a critical error" == caplog.record_tuples[0][2]
    assert len(caplog.record_tuples) == 1


def test_logger_level(caplog):
    with caplog.at_level(logging.DEBUG):
        Logger().set_level(logging.CRITICAL)

        Logger.debug("This is a debug")
        assert len(caplog.record_tuples) == 0

        Logger.info("This is an info")
        assert len(caplog.record_tuples) == 0

        Logger.warning("This is a warning")
        assert len(caplog.record_tuples) == 0

        Logger.error("This is an error")
        assert len(caplog.record_tuples) == 0

        Logger.critical("This is a critical error")
        assert logging.CRITICAL == caplog.record_tuples[0][1]
        assert "This is a critical error" == caplog.record_tuples[0][2]


def test_invalid_handler():
    class _LogHandler(logging.Handler):
        def __init__(self):
            self._log = None
            logging.Handler.__init__(self)

        def emit(self, record):
            self.log = self.format(record)

    handler = _LogHandler()
    handler.setFormatter(ColoredFormatter(False))

    Logger().add_handler(handler)
    Logger.info("Hello from OneCode!")

    log_str = handler.log.split(' - ')
    assert log_str[1] == '|OneCode|.validate_call_decorator.py:81'
    assert log_str[2] == str("Hello from OneCode!")


def test_flush_config_option(caplog):
    Project().set_config(ConfigOption.FLUSH_STDOUT, True)

    Logger().set_level(logging.DEBUG)
    with caplog.at_level(logging.DEBUG):
        Logger.debug("This is a debug")

    assert logging.DEBUG == caplog.record_tuples[0][1]
    assert "This is a debug" == caplog.record_tuples[0][2]
