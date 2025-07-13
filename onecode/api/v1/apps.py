# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import asyncio
from typing import Dict, List, Tuple

from ...base.decorator import check_type
from ..utils import ComputeOptions
from ._concurrent.apps.parameters import async_parameters
from ._concurrent.apps.start import async_start


@check_type
def parameters(
    slug: str
) -> Dict:
    """
    Get the default parameter template for the given app.
    The template is in JSON format and is similar to what you would get
    with `onecode-extract` CLI.
    Edit this template to fit your own parameters before starting a job.

    Args:
        slug: app slug.

    Returns:
        The default parameters as JSON.

    """

    return asyncio.run(
        async_parameters(
            slug
        )
    )


@check_type
def start(
    slug: str,
    output_prefix: str,
    params: Dict,
    files: List[str],
    options: ComputeOptions = {
        "compute_type": "xs",
        "spot": True,
        "timeout": 300,
        "storage": "small"
    }
) -> Tuple[str, int]:
    """
    Run the app with the given parameter set.
    The job ID returned can be used to poll logs and status.
    The reservation lime squeezes returned is the maximum amount of credits that can be used if
    the job goes till the end of the timeout.

    Args:
        slug: app slug.
        output_prefix: path in the storage where outputs will be uploaded.
        params: job parameters, use `api.v1.apps.parameters` to get the default ones.
        files: list of parameter names corresponding to file (as opposed to string, numbers, etc.)
        options: compute options, see `api.utils.ComputeOptions` for details.

    Returns:
        A tuple with the job ID and the lime squeezes reserved.

    """

    return asyncio.run(
        async_start(
            slug,
            output_prefix,
            params,
            files,
            options
        )
    )
