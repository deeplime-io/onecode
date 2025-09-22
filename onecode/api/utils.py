# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from datetime import datetime
from typing import Dict, List, Literal, TypedDict

from dateutil import parser
from rich.console import Console

from ..base.decorator import check_type
from ..base.enums import ConfigOption, Env
from ..base.project import Project

_COLORMAPS = {
    "grey": "bright_cyan"
}

"""
List of possible job status:
- init: the request has been accepted and input data is being prepared
- provisioning: the data preparation is done, the computed server is being provisioned
- running: the job has started, the Python application is launched
- post-processing: job job has finished and outputs are being pushed back to OneCode Cloud
- failed: job has terminated due to errors
- success: job has successfully finished

"""
JOB_STATUS = [
    "init",
    "provisioning",
    "running",
    "post-processing",
    "failed",
    "success"
]


class ComputeOptions(TypedDict):
    """
    Compute options required to start a job
    - compute_type:
        - xs: 1 vCPU | 4 GB RAM
        - s: 2 vCPU | 8 GB RAM
        - m: 4 vCPU | 16 GB RAM
        - l: 8 vCPU | 32 GB RAM
        - xl: 16 vCPU | 64 GB RAM
        - xxl: 16 vCPU | 120 GB RAM
    - spot: True to use cheaper but killable compute if demand is high
    - timout: time in seconds after which the job is killed no matter what
    - storage:
        - small: 20 GB disk size minus the app size
        - large: 200 GB disk size minus the app size

    """

    compute_type: Literal["xs", "s", "m", "l", "xl", "xxl"]
    spot: bool
    timeout: int
    storage: Literal["small", "large"]


def api_url():
    """
    Returns the OneCode Cloud API URL as defined in Project config option under `API_URL`.

    """

    return f'{Project().get_config(ConfigOption.API_URL)}'


def api_token():
    """
    Return the OneCode Cloud API token defined in the `ONECODE_API` env variable
    and format it as headers for HTTP requests.

    """

    return {
        'ONECODE_API': os.environ.get(Env.ONECODE_API_TOKEN, ''),
        'ONECODE_API_TYPE': 'API_KEY'
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
    logs: List[Dict],
    colormap: Dict = _COLORMAPS
):
    """
    Prints the list of log messages to the console.

    Args:
        logs: list of log messages, each message being a dictionnary made of
            `color`, `message` and `timestamp` data.
        colormap: if provided, any color specified in the logs matching one of the colormap
            will be replaced. It allows to handle colors outside the `rich` colorset.
            For instance, the default `_COLORMAPS` replaces any `grey` with `bright_cyan`.

    """

    console = Console(log_time=False, log_path=False)

    for log in logs:
        timestamp = log.get('timestamp', '')
        timestamp = get_datetime(timestamp)

        color = log.get('color', 'white')
        if color in colormap:
            color = colormap[color]

        console.log(f"{timestamp} - {log.get('message')}", style=color)
