# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
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
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Initial text value.
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
            max_chars: Maximum number of characters allowed for this text field.
            placeholder: Placeholder text shown whenever there is no value.
            multiline: Set to True or a height in pixels to make it multiline text area.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `streamlit`, `_value`, etc.

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

    @check_type
    def streamlit(
        self,
        id: str
    ) -> str:
        """
        Returns:
            The Streamlit code for a text input field (`st.text`).

        """
        val = f'"{self.value}"' if self.value is not None else "''"
        default = f'"{self.placeholder}"'
        multiline = self.multiline

        if multiline is False:
            widget = 'st.text_input'
            extra = f'key={id}'
        else:
            widget = 'st.text_area'
            extra = f'''height={"None" if multiline is True else multiline},
    key={id}'''

        return f"""
# Text {self.key}
{self.key} = {widget}(
    {self.label},
    {val},
    disabled={self.disabled},
    max_chars={self.max_chars},
    placeholder={default},
    {extra}
)

"""
