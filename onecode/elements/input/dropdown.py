# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any, List, Optional, Union

from ...base.decorator import check_type
from ..input_element import InputElement


class Dropdown(InputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: Optional[Union[
            Union[str, int, float],
            List[Union[str, int, float]],
            List[List[Union[str, int, float]]]
        ]],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        options: Union[List, str] = [],
        multiple: bool = False,
        **kwargs: Any
    ):
        """
        A single or multipe choice dropdown menu.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Pre-selected value(s) among the options.
            label: Label to display left of the dropdown menu.
            count: Specify the number of occurence of the widget. OneCode typically uses it for the
                UI case. Note that if `count` is defined, the expected `value` should always
                be a list, even if the `count` is `1`. `count` can either be a fixed number
                (e.g. `3`) or an expression dependent of other elements (see
                [Using Expressions][using-runtime-expressions-in-elements] for more information).
            optional: Specify whether the value may be None. `optional` can either be a fixed
                boolean (`False` or `True`) or a conditional expression dependent of other elements
                (see [Using Expressions][using-runtime-expressions-in-elements] for more
                information).
            hide_when_disabled: If element is optional, set it to True to hide it from the
                interface, otherwise it will be shown disabled.
            options: List all possible options available in the dropdown menu. This list may either
                be fixed or dynamic (to a certain extent): in the latter case, use
                [Expressions][using-runtime-expressions-in-elements] in a similar way as `optional`
                and `count`. See example below.
            multiple: Set to True if multiple choice is allowed, otherwise only a single element can
                be selected.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.


        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            Fixed options:
            ```py
            from onecode import dropdown, Mode, Project

            Project().mode = Mode.EXECUTE
            widget = dropdown(
                key="Dropdown",
                value=["A", "C"],
                options=["A", "B", "C"],
                multiple=True
            )
            print(widget)
            ```

            ```py title="Output"
            ["A", "C"]
            ```

            Dynamic options:
            ```
            from onecode import csv_reader, dropdown, Mode, Project

            Project().mode = Mode.EXECUTE

            df = csv_reader("csv", "/path/to/file.csv")

            widget = dropdown(
                key="Dynamic Dropdown",
                value=None,
                options='$csv$.columns',
                optional=True
            )
            print(widget)
            ```

            ```py title="Output"
            None
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
            multiple=multiple,
            **kwargs
        )

    @property
    def _value_type(self) -> type:
        """
        Get the Dropdown value type: either a list of string `list[str]` when the
        Dropdown is multiple choice, otherwise a single string `str`.

        """
        return List[Union[str, int, float]] if self.multiple else Union[str, int, float]

    @check_type
    def _validate_option_value(
        self,
        value: Union[str, int, float]
    ) -> None:
        """
        Raises:
            ValueError: if the value is not part of the possible options.

        !!! note
            This validation is not performed when the option list is dynamic.

        """
        # cannot validate dynamic options
        if not isinstance(self.options, str) and value not in self.options:
            raise ValueError(f"[{self.key}] Not a valid choice: {value}")

    @check_type
    def _validate(
        self,
        value: Union[List[str], str]
    ) -> None:
        """
        Validate the selected value (see
        [`_validate_option_value()`][onecode.elements.input.dropdown.Dropdown._validate_option_value]
        ). In case of multipe choice, each choice is validated individually.

        """
        if self.multiple:
            for v in value:
                self._validate_option_value(v)
        else:
            self._validate_option_value(value)
