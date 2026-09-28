# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from types import UnionType
from typing import Any, Union, get_args, get_origin


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
    if t is Any:
        return True

    origin = get_origin(t)
    if origin is Union or origin is UnionType:
        return any(is_type(obj, arg) for arg in get_args(t))

    if origin is list:
        if not isinstance(obj, list):
            return False
        args = get_args(t)
        if not args or args == (Any,):
            return True
        return all(is_type(item, args[0]) for item in obj)

    try:
        return isinstance(obj, t)
    except TypeError:
        return False
