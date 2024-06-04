# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import pydash
from slugify import slugify

from ..base.decorator import check_type
from ..base.project import Project
from ..utils.typing import is_type


class InputElement(ABC):
    """
    An element is an object that will be interpreted based on the Project's mode (script
    execution, extraction, etc.). OneCode projects should not
    directly call the `InputElement` but its corresponding static function defined as the snake
    case of the element class name. For instance:

    !!! failure
        ```py
        # wrong
        x = MyInputElement(key, value, label)
        ```

    !!! success
        ```py
        # correct
        x = my_input_element(key, value, label)
        ```

    `InputElement` is the base class for input type parameter. By inheriting it, it is mandatory
    to define:

    - [`_value_type`][onecode.InputElement._value_type]: internal attribute to ensure the type of
        the value is correct at runtime.
    - [`_validate()`][onecode.InputElement._validate]: internal method to ensure the value checks
        out at runtime.

    !!! note
        Depending on your case, you may need to subclass `value` too (e.g. like CsvReader
        and FileInput).

    !!! tip
        Don't forget that the Python filename of an element should correspond to the snake case
        form of the element class name (e.g. `FileInput` -> `file_input.py`). You may use
        `pydash` functions `snake_case()` and `pascal_case()` to find the right conversion
        between the two forms.

    Attributes:
        key: Slugified key identifying the element.
        kind: Element class name.
        label: Human readable name typically used for display.
        value: Actual value of the element.
        count: Number of occurence of the element, as a static integer or a dynamic expression.
        optional: Whether the element must return a value or not.
        disabled: The disabled status, as a static boolean or a dynamic expressions.
        hide_when_disabled: Whether the element should be hidden when disabled.

    """

    @check_type
    def __init__(
        self,
        key: str,
        value: Optional[Any],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        **kwargs: Any
    ):
        """
        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Initial value for the parameter. This value may be transformed depending on the
                element.
            label: Typically to be used for display purpose only. If not defined, it
                will default to the `key`.
            count: Placeholder, ignore until we activate this feature.
            optional: Specify whether the `value` may be None.
            hide_when_disabled: Placeholder, ignore until we activate this feature.
            **kwargs: Extra arguments to populate the element with. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        """
        if not key.strip():
            raise ValueError('Key cannot be null')

        elif key.startswith('_'):
            raise ValueError(f'Key starting with "_" are reserved: {key}')

        self._label = label if label is not None else key
        self._key = slugify(key, separator='_')
        self._value = value
        self._count = count
        self._disabled = optional
        self._hide_when_disabled = hide_when_disabled

        reserved_args = dir(self)
        invalid_args = pydash.intersection([*kwargs], [*reserved_args])
        if len(invalid_args) > 0:
            raise AttributeError(f'The following parameters are reserved: {invalid_args}')

        self._extra_args = pydash.omit(kwargs, reserved_args)
        self.__dict__.update(self._extra_args)

    @staticmethod
    def metadata(value: Any) -> Dict:
        """
        Re-implement this function to process the `value` and extract metadata from it.
        By default, it returns an empty dictionnary, meaning no metadata.

        Returns:
            A dictionnary of metadata.

        """
        return {}

    @property
    def kind(self) -> str:
        """
        Returns:
            The element class name.

        """
        return type(self).__name__

    @property
    def key(self) -> str:
        """
        Returns:
            The element key.

        """
        return self._key

    @property
    def label(self) -> str:
        """
        Returns:
            The element label.

        """
        return self._label

    @property
    def value(self) -> Optional[Any]:
        """
        Get the value of the element. By default this value is the one provided during at the
        initialization. Feel free to overwrite this property as required. For instance,
        FileInput and CsvReader re-implement it for their own purpose.

        Returns:
            By default, the same as the initial value.

        """
        return self._value

    @property
    def count(self) -> Union[int, str]:
        """
        Returns:
            The number of occurence of the element (static or dynamic).

        """
        return self._count

    @property
    def optional(self) -> bool:
        """
        Returns:
            The whether the element must return a value or not.

        """
        return isinstance(self._disabled, str) or self._disabled is True

    @property
    def disabled(self) -> Union[bool, str]:
        """
        Returns:
            The element disabling condition.

        """
        return self._disabled

    @property
    def hide_when_disabled(self) -> bool:
        """
        Returns:
            The whether the element should be hidden when disabled.

        """
        return self._hide_when_disabled

    @property
    @abstractmethod
    def _value_type(self) -> type:  # pragma: no cover
        """
        You must re-implement this function to return the expected `type` for the value.
        This `_value_type` is used to check to the proper type at runtime.

        Returns:
            The type of the value (built-in type or typing).

        !!! example
            ```py
            @property
            def _value_type(self) -> type:
                return Union[str, bool]
            ```

        """
        pass

    @abstractmethod
    def _validate(
        self,
        value: Any
    ) -> None:   # pragma: no cover
        """
        You must re-implement this function to validate at runtime the value before being returned
        during the OneCode project execution. This function must raise an error in case the value
        is incorrect/inconsistent wrt the element parameters.

        Args:
            value: Prepared value to be checked (do not use `self.value`).

        !!! example
            For instance, a slider value will fail to validate if it is outside its range:
            ```py
            def _validate(
                self,
                value: Union[float, int]
            ) -> None:
                if self.min > self.max:
                    raise ValueError(
                        f'''[{self.key}] Minimum cannot be greater than maximum:
                        {self.min} > {self.max}'''
                    )

                elif value < self.min:
                    raise ValueError(
                        f'''[{self.key}] Value lower than minimum:
                        {value} < {self.min}'''
                    )

                elif value > self.max:
                    raise ValueError(
                        f'[{self.key}] Value greater than maximum: {value} > {self.max}'
                    )
            ```

        """
        pass

    @check_type
    def _prepare_and_validate(
        self,
        value: Optional[Any]
    ) -> None:
        """
        Internal function used in `Mode.EXECUTE` and `Mode.LOAD_THEN_EXECUTE` to prepare the value,
        check is type, then validate it before returning it.

        Args:
            value: Value to be prepared and validated.

        Raises:
            ValueError: if the value is None but is not optional or the value is of incorrect type.

        """
        if value is None:
            if not self.optional:
                raise ValueError(f"[{self.key}] Value is required: None provided")

        elif self.count is None:
            if is_type(value, self._value_type):
                self._validate(value)
            else:
                raise TypeError(f"Invalid value type for {value}, expected: {self._value_type}")

        else:
            if type(value) is not list:
                raise TypeError(f"Invalid value {value}, expected: list({self._value_type})")

            elif all(is_type(v, self._value_type) for v in value):
                for v in value:
                    self._validate(v)

            else:
                raise TypeError(
                    f"Invalid value type for each element of {value}, expected: {self._value_type}"
                )

    def _console(self) -> 'InputElement':
        """
        Function called when Project mode is `Mode.CONSOLE`.

        Returns:
            This `InputElement` object.

        """
        return self

    def _execute(self) -> Any:
        """
        Function called when Project mode is `Mode.EXECUTE`. The value will first be collected,
        prepared, validated then added to the `Project().data` before being returned.

        Returns:
            The value of this element after resolution (collection, preparation and validation).

        """
        data = Project().data

        if data is None or self.key not in data:
            val = self.value    # actual value after resolution
            Project().add_data(self.key, val)

        else:   # => means: self.key in data
            val = data[self.key]

        self._prepare_and_validate(val)
        return val

    def _load_then_execute(self) -> Any:
        """
        Function called when Project mode is `Mode.LOAD_THEN_EXECUTE`. The value will first be
        collected, prepared, validated then added to the `Project().data` before being returned.

        Returns:
            The value of this element after resolution (collection, preparation and validation).

        """
        data = Project().data

        if self.key not in data:
            val = self.value    # actual value after resolution
            Project().add_data(self.key, val)

        else:
            self._value = data[self.key]
            val = self.value    # resolve the value then use it
            Project().add_data(self.key, val)

        self._prepare_and_validate(val)
        return val

    def _extract(self) -> Tuple[str, Any]:
        """
        Function called when Project mode is `Mode.EXTRACT`. The value will be collected and added
        to the `Project().data` before returning it as key-value object.

        Returns:
            The pair `{ key: value }` of this element.

        """
        data = Project().data

        if data is None or self.key not in data:
            val = self._value   # value set in script
            Project().add_data(self.key, val)

        else:   # => means: self.key in data
            val = Project().data[self.key]

        return self.key, val

    def _extract_all(self) -> Tuple[str, Any]:
        """
        Function called when Project mode is `Mode.EXTRACT_ALL`. The value will be collected and
        added to the `Project().data` before returning it as key-value object along with all
        other element parameters, such as `key`, `kind`, `label`, etc.

        Returns:
            The full parameter set constituting this element as a dictionnary.

        """
        k, v = self._extract()

        params = {
            "key": self.key,
            "kind": self.kind,
            "label": self.label,
            "value": v,
            "count": self.count,
            "optional": self.optional,
            "disabled": self.disabled,
        }
        pydash.merge(params, self._extra_args)

        return k, params

    def dependencies(self) -> List[str]:
        """
        Return the dependent elements used in dynamic expressions if any
        (typicall from `optional`, `count`, etc.).

        """
        deps = set()
        pattern = re.compile(r'\$(.*?)\$')

        for expr in self._dynamic_attributes():
            vars = pattern.findall(str(expr))
            for v in vars:
                deps.add(v)

        return list(deps)

    def _dynamic_attributes(self) -> List[str]:
        """
        Re-implement to expose attributes with potential dynamic expressions.
        By default, `_disabled` and `count` may hold dynamic expressions.

        """
        return [
            self.disabled,
            self.count
        ]

    def _build_gui(self) -> Dict:
        k, p = self._extract_all()

        # if count is None => else return array
        params = {
            **p,
            "metadata": "metadata" in self.__class__.__dict__,
            "depends_on": self.dependencies()
        }

        return k, params

    def __call__(self) -> Any:
        """
        Internal cornerstone for OneCode to distribute the action to perform according to the
        Project mode.

        Raises:
            ValueError: if the Project mode is unknown, e.g. if there is no method matching the
                mode name.

        """

        mode = Project().mode
        if mode in dir(self):
            return getattr(self, mode)()
        else:
            raise ValueError(f"Unknown Project mode {mode}")
