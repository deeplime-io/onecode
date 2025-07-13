# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import asyncio
from datetime import datetime
from typing import Optional

import httpx

from .....base.decorator import check_type
from ...._decorators import with_httpx_client
from ....utils import api_token, api_url


@check_type
@with_httpx_client()
async def async_logs(
    job_id: str,
    after: datetime = None,
    wait: int = None,
    client: Optional[httpx.AsyncClient] = None
):
    status = None

    if wait is not None:
        await asyncio.sleep(wait)

    status_res = await client.get(
        f'{api_url()}/apps/exec/status/{job_id}',
        headers=api_token()
    )
    if not status_res.is_success:
        raise Exception(
            f"{status_res.status_code}: "
            f"{status_res.json().get('error', 'Unknown error')}"
        )
    status = status_res.json().get("job_status")

    logs_res = await client.get(
        f'{api_url()}/apps/exec/logs/{job_id}',
        params={
            "after": after
        },
        headers=api_token()
    )
    if not logs_res.is_success:
        raise Exception(
            f"{logs_res.status_code}: "
            f"{logs_res.json().get('error', 'Unknown error')}"
        )

    logs = logs_res.json().get("logs", [])

    return status, logs
