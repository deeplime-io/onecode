# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any, List, Optional

from ...base.decorator import check_type
from ...base.project import Project
from ..output_element import OutputElement


class FileOutput(OutputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: str,
        label: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any
    ):
        """
        Basic information about the file, such as size and file path.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see
                [examples projects](https://github.com/deeplime-io/onecode/tree/main/examples)).
            value: Path to the output file. Unless absolute, a path is relative to the `outputs`
                folder of the flow currently running.
            label: Typically to be used by Streamlit for display purpose only. If not defined, it
                will default to the `key`.
            tags: Optional meta-data information about the expected file. This information is only
                used when the JSON output attributes are written to the output manifest.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `streamlit`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import file_output, Mode, Project

            Project().mode = Mode.CONSOLE
            widget = file_output(
                key="FileOutput",
                value="/path/to/file.txt",
                label="My FileOutput",
                tags=['TXT']
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
            The Streamlit code to show the basic output file information as text.

        """
        return """
value = os.path.relpath(value)  # allows compat with Windows
if not os.path.exists(value) and not os.path.isfile(value):
    st.warning(f'Invalid file path: {{value}}')

else:
    st.subheader(f'{label} - {os.path.basename(value)}')
    st.info(f'''
File Info\n
- Path: {value}\n
- Size: {round(os.path.getsize(value) / 1e6, 4)} Mo
    ''')
"""
