# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from typing import Any, Optional

import pydash
from slugify import slugify

from ..base.decorator import check_type
from ..base.project import Project


class OutputElement(ABC):
    """
    An element is an object that will be interpreted based on the Project's mode (script
    execution, extraction, etc.). OneCode projects should not
    directly call the `OutputElement` but its corresponding static function defined as the snake
    case of the element class name. For instance:

    !!! failure
        ```py
        # wrong
        x = MyOutputElement(key, value, label)
        ```

    !!! success
        ```py
        # correct
        x = my_output_element(key, value, label)
        ```

    `OutputElement` is the base class for outputs. By inheriting it, it is mandatory to define:

    - [`_validate()`][onecode.OutputElement._validate]: internal method to ensure the value checks
        out at runtime.

    !!! note
        Depending on your case, you may need to subclass `value` too (e.g. like `FileOutput`).

    !!! tip
        Don't forget that the Python filename of an element should correspond to the snake case
        form of the element class name (e.g. `FileOutput` -> `file_output.py`). You may use
        `pydash` functions `snake_case()` and `pascal_case()` to find the right conversion
        between the two forms.

    Attributes:
        key: Slugified key identifying the element.
        kind: Element class name.
        label: Human readable name typically used for display.
        value: Actual value of the element.

        """

    @check_type
    def __init__(
        self,
        key: str,
        value: Any,
        label: Optional[str] = None,
        **kwargs: Any
    ):
        """
        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see
                [examples projects](https://github.com/deeplime-io/onecode/tree/1.x/examples)).
            value: Initial value for the parameter. This value may be transformed depending on the
                element.
            label: Typically to be used for display purpose only. If not defined, it
                will default to the `key`.
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
    def value(self) -> Any:
        """
        Get the value of the element. By default this value is the one provided during at the
        initialization. Feel free to overwrite this property as required. For instance,
        FileOutput re-implements it for its own purpose.

        Returns:
            By default, the same as the initial value.

        """
        return self._value

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
            For instance, an image output value will fail to validate if the file extension is
            not a valid/known extension such as jpeg, png, etc.
            ```py
            def _validate(
                self,
                value: str
            ) -> None:
                _, ext = os.path.splitext(self.value)
                valid_ext = [
                    '.jpg',
                    '.jpeg',
                    '.png',
                    '.svg',
                ]

                if ext.lower() not in valid_ext:
                    raise ValueError(
                        f'''[{self.key}] Invalid image extension:
                        {ext} (accepted: {', '.join(valid_ext)})'''
                    )
            ```

        """
        pass

    def _console(self) -> 'OutputElement':
        """
        Function called when Project mode is `Mode.CONSOLE`.

        Returns:
            This `OutputElement` object.

        """
        return self

    def _execute(self) -> Any:
        """
        Function called when Project mode is `Mode.EXECUTE`. The value will first be prepared,
        validated then all element attributes will be output to the manifest file
        (see [`Project.write_output()`][onecode.Project.write_output]).

        Returns:
            The value of this element after resolution (preparation and validation).

        """
        val = self.value
        self._validate(val)

        params = {
            "key": self.key,
            "label": self._label,
            "value": val,
            "kind": self.kind
        }
        pydash.merge(params, self._extra_args)
        Project().write_output(params)

        return self.value

    def _load_then_execute(self) -> Any:
        """
        Directly returns _execute().

        """
        return self._execute()

    def _extract(self) -> None:
        """
        Nothing is performed: `OutputElement` attributes are not extracted as the actual output
        attributes will be dumped into a manifest file.
        """
        pass

    def _extract_all(self) -> None:
        """
        Nothing is performed: `OutputElement` attributes are not extracted as the actual output
        attributes will be dumped into a manifest file.
        """
        pass

    @staticmethod
    def static_call(cls) -> Optional[Any]:
        """
        Internal cornerstone for OneCode to distribute the action to perform according to the
        Project mode.

        Raises:
            ValueError: if the Project mode is unknown, e.g. if there is no method matching the
                mode name.

        """
        mode = Project().mode
        if mode in dir(cls):
            return getattr(cls, mode)()
        else:
            raise ValueError(f"Unknown Project mode {mode}")

    def __call__(self) -> Optional[Any]:
        """
        Directly returns static_call().

        """
        return self.static_call(self)
