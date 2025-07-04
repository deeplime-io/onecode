# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from datetime import datetime

from dateutil import parser

from ....base.decorator import check_type


@check_type
def get_datetime(
    input: str | int
) -> datetime:
    if isinstance(input, (int, float)):
        if input > 1e11:
            input /= 1000
        input = datetime.fromtimestamp(input)
    else:
        input = parser.parse(input)

    return input
