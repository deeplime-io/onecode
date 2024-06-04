# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any, List, Optional, Union

from ...base.decorator import check_type
from ..input_element import InputElement


class RadioButton(InputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: Optional[Union[str, List[str]]],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        options: List[str] = [],
        horizontal: bool = False,
        **kwargs: Any
    ):
        """
        A single choice represented as a group of exclusive radio buttons.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Radio button initially selected.
            label: Label to display on top of the field.
            count: Placeholder, ignore until we activate this feature.
            optional: Specify whether the `value` may be None.
            hide_when_disabled: Placeholder, ignore until we activate this feature.
            options: List all possible options available.
            horizontal: Set to True to have radio buttons displayed horizontally, otherwise radio
                buttons will be displayed vertically.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            Fixed options:
            ```py
            from onecode import radio_button, Mode, Project

            Project().mode = Mode.EXECUTE
            widget = radio_button(
                key="RadioButton",
                value="A",
                options=["A", "B", "C"]
            )
            print(widget)
            ```

            ```py title="Output"
            "A"
            ```

            Dynamic options:
            ```
            from onecode import csv_reader, radio_button, Mode, Project

            Project().mode = Mode.EXECUTE

            df = csv_reader("csv", "/path/to/file.csv")

            widget = radio_button(
                key="Dynamic RadioButton",
                value=None,
                options='$csv$.columns',
                optional=True
            )

            assert widget is None
            ```

        """
        super().__init__(
            key,
            value,
            label,
            count,
            optional,
            hide_when_disabled,
            options=options,
            horizontal=horizontal,
            **kwargs
        )

    @property
    def _value_type(self) -> type:
        """
        Get the RadioButton value type: string `str`.

        """
        return str

    @check_type
    def _validate(
        self,
        value: str
    ) -> None:
        """
        Raises:
            ValueError: if the choice is not part of possible options.

        """
        if value not in self.options:
            raise ValueError(f"[{self.key}] Not a valid choice: {value}")
