# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any

from typeguard import check_type


def is_type(
    obj: Any,
    t: type
) -> bool:
    """
    Check whether the given object is of a certain type. This function is typically used by
    InputElement to validate values.

    Args:
        obj: Object to test typing against.
        type: Typing to verify: either a built-in type or a Python `typing`.

    Returns:
        True if the object match the type, otherwise False.

    """
    try:
        check_type(value=obj, expected_type=t)
        return True

    except Exception:
        return False
