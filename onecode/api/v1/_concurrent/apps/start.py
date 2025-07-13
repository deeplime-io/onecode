# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Dict, List, Optional

import httpx

from .....base.decorator import check_type
from ...._decorators import with_httpx_client
from ....utils import ComputeOptions, api_token, api_url


@check_type
@with_httpx_client()
async def async_start(
    slug: str,
    output_prefix: str,
    params: Dict,
    files: List[str],
    options: ComputeOptions,
    client: Optional[httpx.AsyncClient] = None
):
    status_res = await client.post(
        f'{api_url()}/apps/exec/start',
        json={
            "slug": slug,
            "output_prefix": output_prefix,
            "params": params,
            "files": files,
            "options": options
        },
        headers=api_token()
    )
    if not status_res.is_success:
        raise Exception(
            f"{status_res.status_code}: "
            f"{status_res.json().get('error', 'Unknown error')}"
        )

    res = status_res.json()

    return (
        res.get("job_id"),
        res.get("reserved_limes")
    )
