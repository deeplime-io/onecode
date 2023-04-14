# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, Union

import pydash
from slugify import slugify

from ..base.decorator import check_type
from ..base.enums import Keyword
from ..base.project import Project
from ..utils.format import convert_expr, indent_block
from ..utils.typing import is_type


class InputElement(ABC):
    """
    An element is an object that will be interpreted based on the Project's mode (script
    execution, extraction, streamlit code generation, etc.). OneCode projects should not
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
    - [`streamlit()`][onecode.InputElement.streamlit]: method returning the Streamlit code to be
        generated.

    !!! note
        Depending on your case, you may need to subclass `value` too (e.g. like CsvReader
        and FileInput).

    !!! tip
        Don't forget that the Python filename of an element should correspond to the snake case
        form of the element class name (e.g. `FileInput` -> `file_input.py`). You may use
        `pydash` functions `snake_case()` and `pascal_case()` to find the right conversion
        between the two forms.

    Attributes:
        label: Human readable name typically used by `streamlit()` for display.
        value: Actual value of the element.
        disabled: The string condition typically used by `streamlit` for disabling the widget.

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
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Initial value for the parameter. This value may be transformed depending on the
                element.
            label: Typically to be used by Streamlit for display purpose only. If not defined, it
                will default to the `key`.
            count: Specify the number of occurence of the widget. OneCode typically uses it for the
                streamlit case. Note that if `count` is defined, the expected `value` should always
                be a list, even if the `count` is `1`. `count` can either be a fixed number
                (e.g. `3`) or an expression dependent of other elements (see
                [Using Expressions][using-runtime-expressions-in-elements] for more information).
            optional: Specify whether the value may be None. `optional` can either be a fixed
                boolean (`False` or `True`) or a conditional expression dependent of other elements
                (see [Using Expressions][using-runtime-expressions-in-elements] for more
                information).
            hide_when_disabled: Only used by Streamlit: if element is optional, set it to True to
                hide it from the interface, otherwise it will be shown disabled.
            **kwargs: Extra arguments to populate the element with. Argument names cannot overwrite
                existing attributes or methods name such as `streamlit`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        """
        if not key.strip():
            raise ValueError('Key cannot be null')

        elif key.startswith('_'):
            raise ValueError(f'Key starting with "_" are reserved: {key}')

        self._label = label if label is not None else key
        self.key = slugify(key, separator='_')
        self._value = value
        self.count = str(count) if isinstance(count, int) else convert_expr(count)
        self.optional = isinstance(optional, str) or optional is True
        self._disabled = 'False' if optional is False \
            else f'_optional_{self.key}' if optional is True \
            else convert_expr(optional)
        self.hide_when_disabled = hide_when_disabled

        reserved_args = dir(self)
        invalid_args = pydash.intersection([*kwargs], [*reserved_args])
        if len(invalid_args) > 0:
            raise AttributeError(f'The following parameters are reserved: {invalid_args}')

        self._extra_args = pydash.omit(kwargs, reserved_args)
        self.__dict__.update(self._extra_args)

    @property
    def kind(self) -> str:
        """
        Returns:
            The element class name.

        """
        return type(self).__name__

    @property
    def label(self) -> str:
        """
        Get the label with triple-quotes and escaped to handle human-readable string.
        It is primarly meant to be directly used in the Streamlit generated code for the
        `label` parameter.
        See [`streamlit()`][onecode.InputElement.streamlit] for more information.

        Returns:
            The string to be used in `streamlit()` for the `label` parameter.

        !!! example
            ```py
            from onecode import Mode, Project, slider

            Project().mode = Mode.CONSOLE
            x = slider("Hello l'aspirateur!", None, optional=True)

            assert x.label == "'''Hello l\\'aspirateur!'''"
            ```

        """
        name = self._label.replace("'", "\\'")
        return f"'''{name}'''"

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
    def disabled(self) -> str:
        """
        Get the whether the element is disabled as a string. It is primarly meant to be
        directly used in the Streamlit generated code for the `disabled` parameter.
        See [`streamlit()`][onecode.InputElement.streamlit] for more information.

        Returns:
            The conditional string to be used in `streamlit()` for the `disabled` parameter.

        """
        return self._disabled

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

    @staticmethod
    def imports() -> List[str]:
        """
        Re-implement this function in case your Streamlit code requires specific Python package
        import. This function should return a list of import statement as string.

        Note that the following packages are already imported (not needed to return them in that
        list): `os`, `json`, `uuid`, `pydash`, `streamlit as st`.

        !!! example
            ```py
            @staticmethod
            def imports() -> List[str]:
                return [
                    "import numpy as np",
                    "import plotly"
                ]
            ```

        """
        return []

    @staticmethod
    def init() -> str:
        """
        Re-implement this function in case your Streamlit code requires specific initialization
        statements. Note that all variables starting with a `_` are reserved.

        !!! example
            ```py
            @staticmethod
            def init() -> str:
                return '''
                    def x(angle):
                        return np.deg2rad(angle%360)
                '''
            ```

        """
        return ''

    @abstractmethod
    def streamlit(
        self,
        id: str
    ) -> str:   # pragma: no cover
        """
        You must re-implement this function to return the expected Streamlit block code for
        this element. This block code will be written out to the generated Streamlit App code.

        Typical attributes that will be useful:
        - `label`: can be directly piped to the Streamlit widget `label` parameter. This attribute
            has been automatically setup for you to use and will properly escape the potential
            troublesome characters.

        - `disabled`: can be directly piped to the Streamlit `disabled` widget parameters. This
            attribute has been automatically setup for you to use and will properly take the
            `optional` argument into account regardless of `optional` being an expression, a
            boolean or None. Therefore, do not use `optional` or `hide_when_disabled`, use
            `disabled` directly.

        - `key`: it must be used as the variable name for the Streamlit widget.

        - all other attributes that are specific to your widget, e.g. `min`, `max`, `step` for
            a Slider, etc.

        Args:
            id: Must be used as the `id` parameter of the Streamlit widget. This variable is
                automatically setup to take uniqueness wrt `count`.

        Returns:
            The Streamlit block code to be output in the generated Streamlit App code.

        !!! example
            ```py
                def streamlit(
                    self,
                    id: str
                ) -> str:

                    return f'''
            # Slider
            {self.key} = st.slider(
                {self.label},
                min_value={self.min},
                max_value={self.max},
                value={self.value},
                step={self.step},
                disabled={self.disabled},
                key={id}
            )

            '''
            ```

        !!! tip
            Remember: no need to use `optional`, `hide_when_disabled` and `count`, they are
            already automatically taken into account to make your life easier. Use `disabled`,
            `label`, `key` and `id`

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
            if self.disabled == 'False':
                raise ValueError(f"[{self.key}] Value is required: None provided")

        elif self.count is None:
            if is_type(value, self._value_type):
                self._validate(value)
            else:
                raise TypeError(f"Invalid value type for {value}, expected: {self._value_type}")

        else:
            if type(value) != list:
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
            "label": self._label,
            "value": v,
            "count": self.count,
            "optional": self.optional,
            "disabled": self.disabled,
        }
        pydash.merge(params, self._extra_args)

        return k, params

    def _build_streamlit(self) -> str:
        """
        Function called when Project mode is `Mode.STREAMLIT`. The Streamlit block code will be
        prepared using the element parameters (such as `count`, `optional`, `hide_when_disabled`,
        etc.) as well as the block code returned by the
        [`streamlit()`][onecode.InputElement.streamlit] function. This function makes it easy to
        extend the `InputElement` without worrying about the `count`, `optional` and
        `hide_when_disabled` attributes.

        Returns:
            The full block code generated by this `InputElement` to be written out to the generated
            Streamlit app code.

        """
        code_gen = ''

        if self.optional and self.disabled == f'_optional_{self.key}':
            code_gen += f"""
_optional_{self.key} = not st.checkbox(
    'Enable ' + {self.label},
    value=True,
    key='_optional_{self.key}'
)
"""

        if self.count is None:
            if self.optional and self.hide_when_disabled:
                code_gen += f"if not ({self.disabled}):"
                code_gen += indent_block(self.streamlit(f"'{self.key}'"))
            else:
                code_gen += self.streamlit(f"'{self.key}'")

            code_gen += f"""
{Keyword.DATA}['{self.key}'] = {self.key} if not ({self.disabled}) else None

"""

        else:
            if self.optional and self.hide_when_disabled:
                inner_code = f"if not ({self.disabled}):"
                inner_code += indent_block(self.streamlit(f"{'f'}'{self.key}_{{_c}}'"), indent=8)
            else:
                inner_code = indent_block(self.streamlit(f"{'f'}'{self.key}_{{_c}}'"))

            code_gen += f"""
{Keyword.DATA}['{self.key}'] = []
for _c in range(int({self.count})):
    {inner_code}
    {Keyword.DATA}['{self.key}'].append({self.key} if not ({self.disabled}) else None)
"""
        return code_gen

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
