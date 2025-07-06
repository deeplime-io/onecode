# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import httpx

from ....utils import api_token, api_url


async def _get_parameters(
    slug: str
):
    async with httpx.AsyncClient() as client:
        status_res = await client.get(
            f'{api_url()}/apps/exec/parameters/{slug}',
            headers=api_token()
        )
        if not status_res.is_success:
            raise Exception(
                f"{status_res.status_code}: "
                f"{status_res.json().get('error', 'Unknown error')}"
            )

        return status_res.json().get("payload")
