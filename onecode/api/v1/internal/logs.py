# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import asyncio
import os
from datetime import datetime

import httpx
from rich.console import Console

from ....base.decorator import check_type
from ....base.enums import ConfigOption, Env
from ....base.project import Project
from .utils import get_datetime

_COLORMAPS = {
    "grey": "bright_cyan"
}


@check_type
async def _get_logs(
    job_id: str,
    after: datetime = None,
    wait: int = None
):
    console = Console(log_time=False)
    status = None
    last_timestamp = None

    if wait is not None:
        await asyncio.sleep(wait)

    async with httpx.AsyncClient() as client:
        status_res = await client.get(
            f'{Project().get_config(ConfigOption.API_URL)}/apps/exec/status/{job_id}',
            headers={'ONECODE_API': os.environ.get(Env.ONECODE_API_TOKEN, '')}
        )
        if not status_res.is_success:
            raise Exception(
                f"{status_res.status_code}: "
                f"{status_res.json().get('error', 'Unknown error')}"
            )
        status = status_res.json().get("job_status")

        logs_res = await client.get(
            f'{Project().get_config(ConfigOption.API_URL)}/apps/exec/logs/{job_id}',
            params={
                "after": after
            },
            headers={'ONECODE_API': os.environ.get(Env.ONECODE_API_TOKEN, '')}
        )
        if not logs_res.is_success:
            raise Exception(
                f"{logs_res.status_code}: "
                f"{logs_res.json().get('error', 'Unknown error')}"
            )

        logs = logs_res.json().get("logs", [])
        for log in logs:
            timestamp = log.get('timestamp', '')
            timestamp = get_datetime(timestamp)

            color = log.get('color', 'white')
            if color in _COLORMAPS:
                color = _COLORMAPS[color]
            console.log(f"{timestamp} - {log.get('message')}", style=color)

            last_timestamp = log.get('timestamp', None)

    if last_timestamp is None:
        last_timestamp = after

    return status, last_timestamp
