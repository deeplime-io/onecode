# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any, List, Optional, Union

from ...base.decorator import check_type
from ..input_element import InputElement


class TextInput(InputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: Optional[Union[str, List[str]]],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        max_chars: int = None,
        placeholder: str = None,
        multiline: Union[bool, int] = False,
        **kwargs: Any
    ):
        """
        A simple text field.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Initial text value.
            label: Label to display on top of the text area.
            count: Placeholder, ignore until we activate this feature.
            optional: Specify whether the `value` may be None.
            hide_when_disabled: Placeholder, ignore until we activate this feature.
            max_chars: Maximum number of characters allowed for this text field.
            placeholder: Placeholder text shown whenever there is no value.
            multiline: Set to True or a height in pixels to make it multiline text area.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import text_input, Mode, Project

            Project().mode = Mode.EXECUTE
            widget = text_input(
                key="TextInput",
                value="OneCode rocks!",
                label="My TextInput"
            )
            print(widget)
            ```

            ```py title="Output"
            "OneCode rocks!"
            ```

        """
        super().__init__(
            key,
            value,
            label,
            count,
            optional,
            hide_when_disabled,
            max_chars=max_chars,
            placeholder=placeholder,
            multiline=multiline,
            **kwargs
        )

    @property
    def _value_type(self) -> type:
        """
        Get the TextInput value type: string `str`.

        """
        return str

    @check_type
    def _validate(
        self,
        value: str
    ) -> None:
        """
        No validation is performed.

        """
        pass
