# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import ast
import os
from typing import Callable

from pydantic import validate_arguments

from .enums import Env


def check_type(func: Callable):  # pragma: no cover
    """
    Decorator forcing type checking at runtime. To control it, run your process with
    the environment variable `ONECODE_DO_TYPECHECK = 1`

    Args:
        func: Function to apply type-checking.

    """
    if (
        Env.ONECODE_DO_TYPECHECK in os.environ and
        bool(ast.literal_eval(os.environ[Env.ONECODE_DO_TYPECHECK]))
    ):
        return validate_arguments(func, config=dict(arbitrary_types_allowed=True))

    return func
