# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any, List, Optional, Union

from ...base.decorator import check_type
from ..input_element import InputElement


def _is_int(x):
    return int(x) == x


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
        step: float = 0.1,
        **kwargs: Any
    ):
        """
        A slider for numerical values.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Initial numerical value.
            label: Label to display on top of the field.
            count: Placeholder, ignore until we activate this feature.
            optional: Specify whether the `value` may be None.
            hide_when_disabled: Placeholder, ignore until we activate this feature.
            min: Mandatory lower bound, defaults to 0.
            max: Mandatory upper bound, defaults to 1.
            step: Mandatory step used when incrementing/decrementing the slider, defaults to 0.1.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.

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
            converted = [float(v) for v in value] if type(value) is list else float(value)

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
            **kwargs
        )

    @property
    def _value_type(self) -> type:
        """
        Get the Slider value type: floating point or integer number `float|int`.

        """
        return Union[float, int]

    @property
    def value(self) -> Optional[Union[float, int, List[float], List[int]]]:
        """
        Get the value of the element as an integer if min, max and steps are all integers.

        """
        int_possible = _is_int(self.max) and _is_int(self.min) and _is_int(self.step)

        if int_possible:
            if type(self._value) is list:
                return [int(v) for v in self._value]

            else:
                return int(self._value)

        return self._value

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
