# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import inspect
from abc import ABC, abstractmethod
from typing import Any, List, Optional

import pydash
from slugify import slugify

from ..base.decorator import check_type
from ..base.project import Project
from ..utils.format import indent_block


class OutputElement(ABC):
    """
    An element is an object that will be interpreted based on the Project's mode (script
    execution, extraction, streamlit code generation, etc.). OneCode projects should not
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
    - [`streamlit()`][onecode.OutputElement.streamlit]: method returning the Streamlit code to be
        generated.

    !!! note
        Depending on your case, you may need to subclass `value` too (e.g. like CsvOutput
        and FileOutput).

    !!! tip
        Don't forget that the Python filename of an element should correspond to the snake case
        form of the element class name (e.g. `FileOutput` -> `file_output.py`). You may use
        `pydash` functions `snake_case()` and `pascal_case()` to find the right conversion
        between the two forms.

    Attributes:
        label: Human readable name typically used by `streamlit()` for display.
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
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see
                [examples projects](https://github.com/deeplime-io/onecode/tree/main/examples)).
            value: Initial value for the parameter. This value may be transformed depending on the
                element.
            label: Typically to be used by Streamlit for display purpose only. If not defined, it
                will default to the `key`.
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
        See [`streamlit()`][onecode.OutputElement.streamlit] for more information.

        Returns:
            The string to be used in `streamlit()` for the `label` parameter.

        !!! example
            ```py
            from onecode import Mode, Project, text_output

            Project().mode = Mode.CONSOLE
            x = text_output("Hello l'aspirateur!", None)

            assert x.label == "'''Hello l\\'aspirateur!'''"
            ```

        """
        name = self._label.replace("'", "\\'")
        return f"'''{name}'''"

    @property
    def value(self) -> Any:
        """
        Get the value of the element. By default this value is the one provided during at the
        initialization. Feel free to overwrite this property as required. For instance,
        FileOutput and CsvOutput re-implement it for their own purpose.

        Returns:
            By default, the same as the initial value.

        """
        return self._value

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

    @staticmethod
    @abstractmethod
    def streamlit() -> str:   # pragma: no cover
        """
        You must re-implement this function to return the expected Streamlit block code for
        this element. This block code will be written out to the generated Streamlit App code.

        You should write this block code as the body of a static function yielding all internal
        attributes (such as `key`, `label`, `value` and `kind`) and any other custom attributes
        provided in this `OutputElement` initialization function's signature.
        For instance:
        ```py
        class MyOutputElement(OutputElement):
            def __init__(
                self,
                key: str,
                value: Any,
                label: Optional[str],
                my_extra_1: int,
                my_extra_2: str
            ):
                # ...
        ```
        will generated the following static function signature
        ```py
        function _MyOutputElement(key, label, value, kind, my_extra_1, my_extra_2)
        ```

        Returns:
            The Streamlit block code to be output in the generated Streamlit App code.

        !!! example
            ```py
                def streamlit() -> str:
                    return '''
            st.write(f'{key} - {label} - {value} - {kind}: {my_extra_1} | {my_extra_2}')
            '''
            ```

            will write out to the Streamlit App file:
            ```py
            # static function called when the corresponding file is selected in the tree
            function _MyOutputElement(key, label, value, kind, my_extra_1, my_extra_2)
                st.write(f'{key} - {label} - {value} - {kind}: {my_extra_1} | {my_extra_2}')
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

    @classmethod
    def _build_streamlit(cls) -> str:
        """
        Function called when Project mode is `Mode.STREAMLIT`. This will generate the output static
        function called when the corresponding output file is selected in the Streamlit App file
        tree. The function signature is made of the internal attributes and any other custom
        attributes.

        !!! note
            See [`streamlit()`][onecode.OutputElement.streamlit] for more information.

        Returns:
            The block code generated by this `OutputElement` to be written out to the generated
            Streamlit app code.

        """
        # Get the _extra_args names to allow them in the function definition to be returned
        # Remove **kwargs from the signature
        extra_args = [*inspect.signature(cls).parameters]
        if extra_args[-1] == "kwargs":
            del extra_args[-1]

        params = pydash.uniq(
            ['key', 'label', 'value', 'kind'] + extra_args
        )

        code_gen = f"""
def _{cls.__name__}({'=None, '.join(params)}=None, **kwargs):
"""
        code_gen += indent_block(cls.streamlit())
        code_gen += "\n"

        return code_gen

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
