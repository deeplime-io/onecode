# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from ...base.decorator import check_type
from ..internal.job_dashboard import _JobDashboard


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
