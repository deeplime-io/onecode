# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import asyncio

from ...base.decorator import check_type
from .internal.job_dashboard import _JobDashboard
from .internal.logs import _get_logs
from .internal.utils import get_datetime


@check_type
def job_dashboard(
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
def job_logs(
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

    status, last_timestamp = asyncio.run(
        _get_logs(
            job_id,
            after
        )
    )

    while keep_streaming and status not in ['failed', 'success']:
        if last_timestamp is not None:
            last_timestamp += 1000

        status, last_timestamp = asyncio.run(
            _get_logs(
                job_id,
                after=last_timestamp,
                wait=3
            )
        )
