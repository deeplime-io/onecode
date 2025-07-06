# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import asyncio
from typing import Dict, List, Tuple

from ...base.decorator import check_type
from ..utils import ComputeOptions, get_datetime, print_logs
from .internal.apps.parameters import _get_parameters
from .internal.apps.start import _start
from .internal.jobs.dashboard import _JobDashboard
from .internal.jobs.logs import _get_logs
from .internal.jobs.status import _get_status


@check_type
def dashboard(
    slug: str,
    max_jobs: int = 10,
    refresh: int = 3
):
    """
    Creates a live dashboard job monitoring for a given app.

    Args:
        slug: app slug.
        max_jobs: maximum jobs to fetch, capped at 50.
        refresh: interval used to refresh the job list.

    """

    _JobDashboard(slug, max_jobs, refresh).run()


@check_type
def logs(
    job_id: str,
    after: int | float = None,
    keep_streaming: bool = True
):
    """
    Get the logs of the given job and print them out.

    Args:
        job_id: ID of the job
        after: only get the logs whose timestamp is after the specified one.
            String datetime will be parsed with dateutil and integers as timestamps.
        keep_streaming: if True and job is still running, keep fetching the logs.

    """

    if after is not None:
        after = get_datetime(after)

    # get initial logs
    status, logs = asyncio.run(
        _get_logs(
            job_id,
            after
        )
    )
    print_logs(logs)

    # if streaming and job is not over, keep fetching logs
    while keep_streaming and status not in ['failed', 'success']:
        if len(logs) > 0:
            if after is None:
                after = 0

            # add 1 micro-sec delta to avoid re-fetching last log
            after = max(after, logs[-1].get('timestamp', 0)) + 1

        status, logs = asyncio.run(
            _get_logs(
                job_id,
                after,
                wait=3
            )
        )
        print_logs(logs)


@check_type
def status(
    job_id: str
) -> str:
    """
    Get the status of the given job. Possible status are listed under
    `api.utils.JOB_STATUS`.

    Args:
        job_id: ID of the job

    Returns:
        The current job status, among the list of `api.utils.JOB_STATUS`.

    """

    return asyncio.run(
        _get_status(
            job_id
        )
    )


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
        _get_parameters(
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
        _start(
            slug,
            output_prefix,
            params,
            files,
            options
        )
    )
