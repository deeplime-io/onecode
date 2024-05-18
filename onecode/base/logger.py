# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import ast
import inspect
import logging
import os
import sys
from typing import Any, Optional

from .decorator import check_type
from .enums import ConfigOption, Env
from .project import Project
from .singleton import Singleton

_do_type_check = (
    Env.ONECODE_DO_TYPECHECK in os.environ and
    bool(ast.literal_eval(os.environ[Env.ONECODE_DO_TYPECHECK]))
)
_logger_stack_level = 6 if _do_type_check else 2
_stack_level = 4 if _do_type_check else 2


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
        format = f"[%(levelname)s] {flow} - %(name)s:%(lineno)d - %(message)s"
        if Project().get_config(ConfigOption.LOGGER_TIMESTAMP):
            format = f"%(asctime)s {format}"

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
        self.reset(False)

    def reset(
        self,
        root_logger: bool = True
    ) -> None:
        """
        Remove all added handlers attached to the OneCode logger and optionally
        the root logger if specified (see `logging.removeHandler()` for more info).
        OneCode logger is then reset to the default console stream handler with the
        [ColoredFormatter][onecode.ColoredFormatter] with `INFO` level.

        Args:
            root_logger: If True, remove the handlers from the root logger too,
                in addition to removing the handlers from OneCode logger.

        """
        namespaces = [Env.ONECODE_LOGGER_NAME]
        if root_logger:
            namespaces.append(None)

        for n in namespaces:
            logger = logging.getLogger(n)
            while len(logger.handlers) > 0:
                logger.removeHandler(logger.handlers[0])

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColoredFormatter(Project().get_config(ConfigOption.LOGGER_COLOR)))
        logging.getLogger(Env.ONECODE_LOGGER_NAME).addHandler(handler)
        self.set_level(logging.INFO)

    @check_type
    def add_handler(
        self,
        handler: Optional[logging.Handler] = None,
        root_logger: bool = True
    ) -> None:
        """
        Add an extra handler in addition to the default console stream one.
        Nothing is done if handler is None.

        Args:
            handler: New handler to add.
            root_logger: If True, add the handler at the root logging, otherwise
                as a child of the `|OneCode|` logger.

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
            namespace = Env.ONECODE_LOGGER_NAME if not root_logger else None
            logging.getLogger(namespace).addHandler(handler)

    @check_type
    def set_level(
        self,
        level: int
    ) -> None:
        """
        Set the OneCode logger level. Default logging is INFO.

        Args:
            level: Numerical value to set the logging level to. See
                [logging levels](https://docs.python.org/3/library/logging.html#logging-levels) for
                more information.

        """
        logging.getLogger(Env.ONECODE_LOGGER_NAME).setLevel(level)

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
        return logging.getLogger(f'{Env.ONECODE_LOGGER_NAME}.{file}')

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
    def debug(msg: Any) -> None:
        """
        Convenience function to log a debug message.

        Args:
            msg: Message to log.

        """
        Logger().logger(_logger_stack_level).debug(msg, stacklevel=_stack_level)
        Logger._flush()

    @staticmethod
    @check_type
    def info(msg: Any) -> None:
        """
        Convenience function to log an info message.

        Args:
            msg: Message to log.

        """
        Logger().logger(_logger_stack_level).info(msg, stacklevel=_stack_level)
        Logger._flush()

    @staticmethod
    @check_type
    def warning(msg: Any) -> None:
        """
        Convenience function to log a warning message.

        Args:
            msg: Message to log.

        """
        Logger().logger(_logger_stack_level).warning(msg, stacklevel=_stack_level)
        Logger._flush()

    @staticmethod
    @check_type
    def error(msg: Any) -> None:
        """
        Convenience function to log an error message.

        Args:
            msg: Message to log.

        """
        Logger().logger(_logger_stack_level).error(msg, stacklevel=_stack_level)
        Logger._flush()

    @staticmethod
    @check_type
    def critical(msg: Any) -> None:
        """
        Convenience function to log a critical message.

        Args:
            msg: Message to log.

        """
        Logger().logger(_logger_stack_level).critical(msg, stacklevel=_stack_level)
        Logger._flush()
