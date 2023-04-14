# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from typing import Any, List, Optional, Union

from ...base.decorator import check_type
from ...base.project import Project
from ...utils.typing import is_type
from ..input_element import InputElement


class FolderInput(InputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: Optional[Union[str, List[str]]],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        **kwargs: Any
    ):
        """
        A single folder selector.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Path to folder. Provided folder doesn't necessarily have to exist for the
                Streamlit mode, however its existence will be checked at execution time. If path
                is not absolute, then it is considered relative to the data root folder. See
                [Best Practices With Data][best-practices-with-data] for more information.
            label: Label to display left of the folder selector.
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
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `streamlit`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import folder_input, Mode, Project

            Project().mode = Mode.EXECUTE
            widget = folder_input(
                key="FolderInput",
                value="/path/to/"
            )
            print(widget)
            ```

            ```py title="Output"
            "/path/to/"
            ```

        """
        super().__init__(
            key,
            value,
            label,
            count,
            optional,
            hide_when_disabled,
            **kwargs
        )

    @property
    def _value_type(self) -> type:
        """
        Get the FolderInput value type: a single string `str`.

        """
        return str

    @property
    def value(self) -> Optional[str]:
        """
        Returns:
            The path or list of paths for the selected folder: if paths are not absolute, then
            they are considered relative to the data root folder. See
            [Best Practices With Data][best-practices-with-data] for more information.

        """
        if self._value is not None:
            if is_type(self._value, self._value_type):
                return Project().get_input_path(self._value)

            elif type(self._value) == list and all(
                is_type(v, self._value_type) for v in self._value
            ):
                return [
                    Project().get_input_path(val) for val in self._value
                ]

        return None

    @check_type
    def _validate(
        self,
        value: str
    ) -> None:
        """
        Raises:
            FileNotFoundError: if the path does not exist or is not a folder.

        """
        if not os.path.exists(value):
            raise FileNotFoundError(f"[{self.key}] Folder not found: {value}")
        if not os.path.isdir(value):
            raise NotADirectoryError(f"[{self.key}] Path is not a folder: {value}")

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
            The Streamlit code for a folder selection (`st.text_input` for the path combined with a
            `tkinter.filedialog.askdirectory` for the file selection).

        """
        label = self.label
        key = self.key

        button_key = f'_button_{key}'
        file_key = f'_file_{key}'
        file_id = f'"_file_" + {id}'

        # if there is a count, it's too complicated to set defaults
        # => so default to None
        if self.value is not None and self.count is None:
            value = f"'''{self.value}'''"
        else:
            value = 'None'

        return f"""
# FolderInput {key}
left, right = st.columns([3, 1])
with right:
    {button_key} = right.button('Select folder', disabled={self.disabled}, key="button_" + {id})

{file_key} = st.session_state[{file_id}] if {file_id} in st.session_state else {value}
if {button_key}:
    {file_key} = filedialog.askdirectory(
        master=_root,
        title='Select folder'
    )
    st.session_state[{file_id}] = {file_key}

with left:
    {key} = left.text_input({label}, {file_key}, disabled={self.disabled}, key={id})
"""
