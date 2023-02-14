# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import List, Optional, Union

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
        hide_when_disabled: bool = False
    ):
        """
        A simple checkbox with a label. Value is either True, False or None.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Initial check status: True, False or None.
            label: Label to display next to the checkbox.
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
            hide_when_disabled
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

    @check_type
    def streamlit(
        self,
        id: str
    ) -> str:
        """
        Returns:
            The Streamlit code for a checkbox (`st.checkbox`).

        """
        return f"""
# Checkbox {self.key}
{self.key} = st.checkbox(
    {self.label},
    {self.value},
    disabled={self.disabled},
    key={id}
)

"""
