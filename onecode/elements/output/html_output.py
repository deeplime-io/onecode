# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from typing import Any, List, Optional

from ...base.decorator import check_type
from ...base.project import Project
from ..output_element import OutputElement


class HtmlOutput(OutputElement):
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
        Link to HTML file opening in a new tab.

        Args:
            key: ID of the element. It must be unique as it is the key used to store data in
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
            from onecode import html_output, Mode, Project

            Project().mode = Mode.EXECUTE
            Project().current_flow = 'test'

            file = html_output(
                key="HtmlOutput",
                value="/path/to/file.html",
                label="My HtmlOutput",
                tags=['HTML']
            )

            with open(file, 'w') as f:
                f.write('<html><body>Hello OneCode!</body></html>')

            print(file)
            ```

            ```py title="Output"
            "/path/to/file.html"
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
            The path to the output file: if path are not absolute, then it is considered relative
            to the data output folder. See [Best Practices With Data][best-practices-with-data]
            for more information.

        """
        return Project().get_output_path(self._value)

    @check_type
    def _validate(
        self,
        value: str
    ) -> None:
        """
        Raises:
            ValueError: if the file does not have a HTML extension, i-e: `.html`.

        """
        _, ext = os.path.splitext(self.value)
        valid_ext = [
            '.html',
        ]

        if ext.lower() not in valid_ext:
            raise ValueError(
                f"[{self.key}] Invalid file extension: {ext} (accepted: {', '.join(valid_ext)})"
            )
