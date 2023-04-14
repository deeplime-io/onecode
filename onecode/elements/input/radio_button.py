# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any, List, Optional, Union

import pydash

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
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Radio button initially selected.
            label: Label to display on top of the field.
            count: Specify the number of occurence of the widget. OneCode typically uses it for the
                streamlit case. Note that if `count` is defined, the expected `value` should always
                be a list, even if the `count` is `1`. `count` can either be a fixed number
                (e.g. `3`) or an expression dependent of other elements (see
                [Using Expressions][using-runtime-expressions-in-elements] for more information).
            optional: Specify whether the value may be None. `optional` can either be a fixed
                boolean (`False` or `True`) or a conditional expression dependent of other elements
                (see [Using Expressions][using-runtime-expressions-in-elements] for more
                information).
            hide_when_disabled: If element is optional, set it to True to hide it from the
                interface, otherwise it will be shown disabled.
            options: List all possible options available. This list may either be fixed or dynamic
                (to a certain extent): in the latter case, use expressions in a similar  way as
                `optional` and `count`. See example below.
            horizontal: Set to True to have radio buttons displayed horizontally, otherwise radio
                buttons will be displayed vertically.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `streamlit`, `_value`, etc.

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

    @check_type
    def streamlit(
        self,
        id: str
    ) -> str:
        """
        Returns:
            The Streamlit code for a group of radio buttons (`st.radio`).

        """
        return f"""
# RadioButton {self.key}
{self.key} = st.radio(
    {self.label},
    options={self.options},
    index={pydash.find_index(self.options, lambda x: x == self.value)},
    disabled={self.disabled},
    horizontal={self.horizontal},
    key={id}
)

"""
