# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Dict, List

import httpx

from ....utils import ComputeOptions, api_token, api_url


async def async_start(
    slug: str,
    output_prefix: str,
    params: Dict,
    files: List[str],
    options: ComputeOptions
):
    async with httpx.AsyncClient() as client:
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
