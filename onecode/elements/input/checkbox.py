# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any, List, Optional, Union

from ...base.decorator import check_type
from ..input_element import InputElement


class Checkbox(InputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: Optional[Union[bool, List[bool]]],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        **kwargs: Any
    ):
        """
        A simple checkbox with a label. Value is either True, False or None.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Initial check status: True, False or None.
            label: Label to display next to the checkbox.
            count: Placeholder, ignore until we activate this feature.
            optional: Specify whether the `value` may be None.
            hide_when_disabled: Placeholder, ignore until we activate this feature.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import checkbox, Mode, Project

            Project().mode = Mode.EXECUTE
            widget = checkbox(
                key="Checkbox",
                value=True,
                label="My Checkbox"
            )
            print(widget)
            ```

            ```py title="Output"
            True
            ```

        """
        super().__init__(
            key,
            value,
            label,
            count,
            optional,
            hide_when_disabled,
            **kwargs
        )

    @property
    def _value_type(self) -> type:
        """
        Get the Checkbox value type: boolean `bool`.

        """
        return bool

    @check_type
    def _validate(
        self,
        value: bool
    ) -> None:
        """
        No validation is performed.

        """
        pass
