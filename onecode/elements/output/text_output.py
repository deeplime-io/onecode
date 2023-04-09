# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any, List, Optional

from ...base.decorator import check_type
from ...base.project import Project
from ..output_element import OutputElement


class TextOutput(OutputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: str,
        label: Optional[str] = None,
        tags: Optional[List[str]] = None,
        truncate_at: int = 50000,
        **kwargs: Any
    ):
        """
        A text file preview.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see
                [examples projects](https://github.com/deeplime-io/onecode/tree/main/examples)).
            value: Path to the output CSV file which must have a `.csv` extension. Unless absolute,
                a path is relative to the `outputs` folder of the flow currently running.
            label: Typically to be used by Streamlit for display purpose only. If not defined, it
                will default to the `key`.
            tags: Optional meta-data information about the expected file. This information is only
                used when the JSON output attributes are written to the output manifest.
            truncate_at: Truncate the preview at the specified number of characters.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `streamlit`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import text_output, Mode, Project

            Project().mode = Mode.CONSOLE
            widget = text_output(
                key="TextOutput",
                value="/path/to/file.txt",
                label="My TextOutput",
                tags=['Text'],
                truncate_at=1000
            )
            print(widget)
            ```

            ```py title="Output"
            "/path/to/file.txt"
            ```

        """
        super().__init__(
            key,
            value,
            label,
            tags=tags,
            truncate_at=truncate_at,
            **kwargs
        )

    @property
    def value(self) -> str:
        """
        Returns:
            The path or list of paths for the output file(s): if paths are not absolute, then
            they are considered relative to the data output folder. See
            [Best Practices With Data][best-practices-with-data] for more information.

        """
        return Project().get_output_path(self._value)

    @check_type
    def _validate(
        self,
        value: str
    ) -> None:
        """
        No validation is performed.

        """
        pass

    @staticmethod
    def streamlit() -> str:
        """
        Returns:
            The Streamlit code to preview text of a file.

        """
        return """
value = os.path.relpath(value)  # allows compat with Windows
if not os.path.exists(value) and not os.path.isfile(value):
    st.warning(f'Invalid file path: {{value}}')

else:
    with open(value, 'r') as f:
        txt = f.read()

    if len(txt) > truncate_at:
        txt = txt[:truncate_at]
        st.warning(f'File trucated at {truncate_at} characters')

    st.subheader(f'{label} - {os.path.basename(value)}')
    st.code(txt)
"""
