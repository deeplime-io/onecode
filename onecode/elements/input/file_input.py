# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from typing import Any, List, Optional, Tuple, Union

from ...base.decorator import check_type
from ...base.project import Project
from ...utils.typing import is_type
from ..input_element import InputElement


class FileInput(InputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: Optional[Union[str, List[str], List[List[str]]]],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        types: List[Tuple[str, str]] = None,
        multiple: bool = False,
        tags: Optional[List[str]] = None,
        **kwargs: Any
    ):
        """
        A single or multiple file selector.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Path to file(s). Provided file(s) don't necessarily have to exist for the
                Streamlit mode, however their existence will be checked at execution time. If paths
                are not absolute, then they are considered relative to the data root folder. See
                [Best Practices With Data][best-practices-with-data] for more information.
            label: Label to display left of the file selector.
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
            types: List of filters allowing to narrow file selection within Streamlit. Each filter
                must be a pair of (name, list of allowed extensions), e.g.
                `("Image", ".jpg .png .jpeg")`. You may use the FileFilter enums for convenience.
            multiple: Set to True if multiple choice is allowed, otherwise only a single element can
                be selected.
            tags: Optional meta-data information about the expected file. This information is only
                used by the `Mode.EXTRACT_ALL` when dumping attributes to JSON.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `streamlit`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import file_input, Mode, Project

            Project().mode = Mode.EXECUTE
            widget = file_input(
                key="FileInput",
                value=["/path/to/file1.txt", "/path/to/file2.csv"],
                multiple=True,
                tags=['MyTags']
            )
            print(widget)
            ```

            ```py title="Output"
            ["/path/to/file1.txt", "/path/to/file2.csv"]
            ```

        """
        super().__init__(
            key,
            value,
            label,
            count,
            optional,
            hide_when_disabled,
            types=types,
            multiple=multiple,
            tags=tags,
            **kwargs
        )

    @property
    def _value_type(self) -> type:
        """
        Get the FileInput value type: either a list of string `list[str]` when the
        FileInput is multiple file selection, otherwise a single string `str`.

        """
        return List[str] if self.multiple else str

    @property
    def value(self) -> Optional[Union[List[str], str]]:
        """
        Returns:
            The path or list of paths for the selected file(s): if paths are not absolute, then
            they are considered relative to the data root folder. See
            [Best Practices With Data][best-practices-with-data] for more information.

        """
        if self._value is not None:
            if is_type(self._value, self._value_type):
                return [Project().get_input_path(f) for f in self._value] if self.multiple \
                    else Project().get_input_path(self._value)

            elif type(self._value) == list and all(
                is_type(v, self._value_type) for v in self._value
            ):
                return [
                    [Project().get_input_path(f) for f in val] if self.multiple
                    else Project().get_input_path(val) for val in self._value
                ]

        return None

    @check_type
    def _validate_file_value(
        self,
        value: str
    ) -> None:
        """
        Raises:
            FileNotFoundError: if the path does not exist or is not a file.

        """
        if not os.path.exists(value):
            raise FileNotFoundError(f"[{self.key}] File not found: {value}")

        elif not os.path.isfile(value):
            raise FileNotFoundError(f"[{self.key}] Path is not a file: {value}")

    @check_type
    def _validate(
        self,
        value: Union[List[str], str]
    ) -> None:
        """
        Validate the selected value (see _validate_option_value()). In case of multipe file
        selection, each choice is validated individually.

        """
        if self.multiple:
            for v in value:
                self._validate_file_value(v)
        else:
            self._validate_file_value(value)

    @staticmethod
    def imports() -> List[str]:
        """
        Returns:
            Python import statements required by the Streamlit code.

        """
        return [
            "import tkinter as tk",
            "from tkinter import filedialog"
        ]

    @staticmethod
    def init() -> str:
        """
        Returns:
            The Python statements that must be initialized before being used by the Streamlit code.

        """
        return """_root = tk.Tk()
_root.withdraw()
_root.wm_attributes('-topmost', 1)
"""

    @check_type
    def streamlit(
        self,
        id: str
    ) -> str:
        """
        Returns:
            The Streamlit code for a file selection (`st.text_input` for the path combined with a
            `tkinter.filedialog.askopenfilename` for the file selection).

        """
        label = self.label
        key = self.key
        types = [] if self.types is None else self.types

        mtp = 's' if self.multiple else ''
        button_key = f'_button_{key}'
        file_key = f'_file_{key}'
        file_id = f'"_file_" + {id}'

        # if there is a count, it's too complicated to set defaults
        # => so default to None
        if self.value is not None and self.count is None:
            value = tuple(self.value) if self.multiple else f"'''{self.value}'''"
        else:
            value = 'None'

        return f"""
# FileInput {key}
left, right = st.columns([3, 1])
with right:
    {button_key} = right.button('Select file{mtp}', disabled={self.disabled}, key="button_" + {id})

{file_key} = st.session_state[{file_id}] if {file_id} in st.session_state else {value}
if {button_key}:
    {file_key} = filedialog.askopenfilename{mtp}(
        master=_root,
        filetypes={types},
        title='Select file{mtp}'
    )
    st.session_state[{file_id}] = {file_key}

with left:
    {key} = left.text_input({label}, {file_key}, disabled={self.disabled}, key={id})
    if {self.multiple} and {key} is not None: # is multiple?
        {key} = ast.literal_eval({key})
        if {key} is not None:
            {key} = list({key})

"""
