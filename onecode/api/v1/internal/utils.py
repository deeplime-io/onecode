# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from datetime import datetime
from typing import List, Dict
from rich.console import Console

from dateutil import parser

from ....base.decorator import check_type


_COLORMAPS = {
    "grey": "bright_cyan"
}


@check_type
def get_datetime(
    input: str | int
) -> datetime:
    """
    
    """
    
    try:
        if isinstance(input, (int, float)):
            if input > 1e11:
                input /= 1000
            input = datetime.fromtimestamp(input)
        else:
            input = parser.parse(input)
    except:
        pass

    return input


@check_type
def print_logs(
    logs: List[Dict]
):
    """
    
    """
    
    console = Console(log_time=False, log_path=False)

    for log in logs:
        timestamp = log.get('timestamp', '')
        timestamp = get_datetime(timestamp)

        color = log.get('color', 'white')
        if color in _COLORMAPS:
            color = _COLORMAPS[color]

        console.log(f"{timestamp} - {log.get('message')}", style=color)
