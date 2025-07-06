# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import asyncio

from ...base.decorator import check_type
from ..utils import get_datetime, print_logs
from .internal.job_dashboard import _JobDashboard
from .internal.logs import _get_logs
from .internal.status import _get_status


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
):
    """
    Get the status of the given job. Possible status are listed under `JOB_STATUS`.

    Args:
        job_id: ID of the job

    Returns:
        The current job status, among the list of `JOB_STATUS`.

    """

    return asyncio.run(
        _get_status(
            job_id
        )
    )
