# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from datetime import datetime
from typing import Dict, List

from dateutil import parser
from rich.console import Console

from ....base.decorator import check_type

_COLORMAPS = {
    "grey": "bright_cyan"
}


@check_type
def get_datetime(
    input: str | int
) -> datetime:
    """
    Get the datetime from Unix Epoch timestamp (int) or date-like string (e.g. ISO, UTC, etc.).
    If parsing fails, it returns the original input.

    Args:
        input: datetime to parse, use int for Unix Epoch timestamp or string for other datetimes.

    Returns:
        The converted value as Datetime object if successful, the original input otherwise.
    """

    original = input
    try:
        if isinstance(input, (int, float)):
            if input > 1e11:
                input /= 1000
            input = datetime.fromtimestamp(input)
        else:
            input = parser.parse(input)
    except Exception:
        return original

    return input


@check_type
def print_logs(
    logs: List[Dict]
):
    """
    Prints the list of log messages to the console.

    Args:
        logs: list of log messages, each message being a dictionnary made of
            `color`, `message` and `timestamp` data.
    """

    console = Console(log_time=False, log_path=False)

    for log in logs:
        timestamp = log.get('timestamp', '')
        timestamp = get_datetime(timestamp)

        color = log.get('color', 'white')
        if color in _COLORMAPS:
            color = _COLORMAPS[color]

        console.log(f"{timestamp} - {log.get('message')}", style=color)
