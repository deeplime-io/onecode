# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Optional

import httpx

from .....base.decorator import check_type
from ...._decorators import with_httpx_client
from ....utils import api_token, api_url


@check_type
@with_httpx_client()
async def async_status(
    job_id: str,
    client: Optional[httpx.AsyncClient] = None
):
    status_res = await client.get(
        f'{api_url()}/apps/exec/status/{job_id}',
        headers=api_token()
    )
    if not status_res.is_success:
        raise Exception(
            f"{status_res.status_code}: "
            f"{status_res.json().get('error', 'Unknown error')}"
        )

    return status_res.json().get("job_status")
