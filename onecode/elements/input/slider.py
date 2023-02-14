# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import List, Optional, Union

from ...base.decorator import check_type
from ..input_element import InputElement


class Slider(InputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: Optional[Union[float, List[float]]],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        min: float = 0.,
        max: float = 1.,
        step: float = 0.1
    ):
        """
        A slider for numerical values.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Initial numerical value.
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
            min: Mandatory lower bound, defaults to 0.
            max: Mandatory upper bound, defaults to 1.
            step: Mandatory step used when incrementing/decrementing the slider, defaults to 0.1.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import slider, Mode, Project

            Project().mode = Mode.EXECUTE
            widget = slider(
                key="Slider",
                value=5.1,
                min=5,
                max=6
            )
            print(widget)
            ```

            ```py title="Output"
            5.1
            ```

        """
        # cast to float in case int is provided
        converted = None
        if value is not None:
            converted = [float(v) for v in value] if type(value) == list else float(value)

        super().__init__(
            key,
            converted,
            label,
            count,
            optional,
            hide_when_disabled,
            min=float(min),
            max=float(max),
            step=float(step),
        )

    @property
    def _value_type(self) -> type:
        """
        Get the Slider value type: floating point or integer number `float|int`.

        """
        return Union[float, int]

    @check_type
    def _validate(
        self,
        value: Union[float, int]
    ) -> None:
        """
        Raises:
            ValueError: if the value is out of bound (min/max) or if the minimum is greather than
                the maximum.

        """
        if self.min > self.max:
            raise ValueError(
                f"[{self.key}] Minimum cannot be greater than maximum: {self.min} > {self.max}"
            )

        elif value < self.min:
            raise ValueError(f"[{self.key}] Value lower than minimum: {value} < {self.min}")

        elif value > self.max:
            raise ValueError(f"[{self.key}] Value greater than maximum: {value} > {self.max}")

    @check_type
    def streamlit(
        self,
        id: str
    ) -> str:
        """
        Returns:
            The Streamlit code for a slider (`st.slider`).

        """
        return f"""
# Slider {self.key}
{self.key} = st.slider(
    {self.label},
    min_value={self.min},
    max_value={self.max},
    value={self.value},
    step={self.step},
    disabled={self.disabled},
    key={id}
)

"""
