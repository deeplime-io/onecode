# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import inspect
import logging
import os
import sys
from typing import Optional

from .decorator import check_type
from .enums import ConfigOption
from .project import Project
from .singleton import Singleton


class ColoredFormatter(logging.Formatter):
    """
    Logger class formatting messages in a specific way with colors interpretable
    by the terminal/console according to the log level:

    - `DEBUG` and `INFO`: grey
    - `WARNING`: yellow
    - `ERROR`: red
    - `CRITICAL`: bold red

    Message is formatted like this:
    ```bash
    timestamp [log_level] current_flow_name - filename:LOC - actual_message
    ```

    """

    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    @check_type
    def __init__(
        self,
        color: bool = True
    ):
        super().__init__()
        self._color = color

    @check_type
    def format(
        self,
        record: logging.LogRecord
    ) -> str:
        """
        Format the given record

        Args:
            record: Record passing through the formatter. See
                [Python logging](https://docs.python.org/3/library/logging.html#formatter-objects)
                for more info.

        Returns:
            The formatted text.

        """
        flow = Project().current_flow if Project().current_flow is not None else ''
        format = f"%(asctime)s [%(levelname)s] {flow} - %(name)s:%(lineno)d - %(message)s"

        formats = {
            logging.DEBUG: f"{self.GREY}{format}{self.RESET}",
            logging.INFO: f"{self.GREY}{format}{self.RESET}",
            logging.WARNING: f"{self.YELLOW}{format}{self.RESET}",
            logging.ERROR: f"{self.RED}{format}{self.RESET}",
            logging.CRITICAL: f"{self.BOLD_RED}{format}{self.RESET}",
        }

        log_fmt = formats.get(record.levelno) if self._color else format
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger(metaclass=Singleton):
    """
    Single Logger object to handle Python logging within OneCode projects.
    The default logging level is INFO. See [`set_level()`][onecode.Logger.set_level] to change it.
    Use the static methods [`debug()`][onecode.Logger.debug], [`info()`][onecode.Logger.info],
    [`warning()`][onecode.Logger.warning], [`error()`][onecode.Logger.error], and
    [`critical()`][onecode.Logger.critical] to conveniently log your messages with the
    corresponding logging level.

    By default, the ColoredFormatter is used. You may add other logging handlers using
    [`add_handler()`][onecode.Logger.add_handler], for instance to redirect logs to a file.

    !!! example
        ```py
        import logging
        from onecode import Logger

        Logger().set_level(logging.DEBUG)

        Logger.debug("debug")
        Logger.info("info")
        Logger.warning("warning")
        Logger.error("error")
        Logger.critical("critical")
        ```

    """

    def __init__(self):
        self.set_level(logging.INFO)
        self.reset()

    def reset(self) -> None:
        """
        Remove all added handlers attached to the logger (see `logging.removeHandler()` for more
        info) and reset to the default console stream handler with the
        [ColoredFormatter][onecode.ColoredFormatter].

        """
        logger = logging.getLogger()
        while logger.hasHandlers():
            logger.removeHandler(logger.handlers[0])

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColoredFormatter())
        logging.getLogger().addHandler(handler)

    @check_type
    def add_handler(
        self,
        handler: Optional[logging.Handler] = None
    ) -> None:
        """
        Add an extra handler in addition to the default console stream one.
        Nothing is done if handler is None.

        Args:
            handler: New handler to add.


        !!! example
            ```py
            import logging

            from onecode import Logger


            handler = logging.FileHandler("debug.log")
            Logger().add_handler(handler)
            Logger.error('oops!')   # will print to console in red and to file "debug.log"
            ```

        """
        if handler is not None:
            logging.getLogger().addHandler(handler)

    @check_type
    def set_level(
        self,
        level: int
    ) -> None:
        """
        Set the logger level. Default logging is INFO.

        Args:
            level: Numerical value to set the logging level to. See
                [logging levels](https://docs.python.org/3/library/logging.html#logging-levels) for
                more information.

        """
        logging.getLogger().setLevel(level)

    @check_type
    def logger(
        self,
        stacklevel: int = 1,
    ) -> logging.Logger:
        """
        Get the Python Logger object corresponding to the given stack level. Preferentially use
        convenience methods [`debug()`][onecode.Logger.debug], [`info()`][onecode.Logger.info],
        [`warning()`][onecode.Logger.warning], [`error()`][onecode.Logger.error], and
        [`critical()`][onecode.Logger.critical].

        Args:
            stacklevel: Number of hops back in the function call stack to tie the logger to.
                By default, it is the last function calling this logger() method.

        Returns:
            Python Logger object.

        """
        stack = inspect.stack()
        file = os.path.basename(stack[stacklevel].filename) if len(stack) > stacklevel else None
        return logging.getLogger(file)

    @staticmethod
    def _flush() -> None:
        """
        Force flush to stdout if `ConfigOption.FLUSH_STDOUT` is True. See
            [Project.config][onecode.Project.config] for more information.

        """
        if Project().get_config(ConfigOption.FLUSH_STDOUT):
            sys.stdout.flush()

    @staticmethod
    @check_type
    def debug(msg: str) -> None:
        """
        Convenience function to log a debug message.

        Args:
            msg: Message to log.

        """
        Logger().logger(2).debug(msg, stacklevel=2)
        Logger._flush()

    @staticmethod
    @check_type
    def info(msg: str) -> None:
        """
        Convenience function to log an info message.

        Args:
            msg: Message to log.

        """
        Logger().logger(2).info(msg, stacklevel=2)
        Logger._flush()

    @staticmethod
    @check_type
    def warning(msg: str) -> None:
        """
        Convenience function to log a warning message.

        Args:
            msg: Message to log.

        """
        Logger().logger(2).warning(msg, stacklevel=2)
        Logger._flush()

    @staticmethod
    @check_type
    def error(msg: str) -> None:
        """
        Convenience function to log an error message.

        Args:
            msg: Message to log.

        """
        Logger().logger(2).error(msg, stacklevel=2)
        Logger._flush()

    @staticmethod
    @check_type
    def critical(msg: str) -> None:
        """
        Convenience function to log a critical message.

        Args:
            msg: Message to log.

        """
        Logger().logger(2).critical(msg, stacklevel=2)
        Logger._flush()
