# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import mimetypes
import os
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
        make_path: bool = False,
        **kwargs: Any
    ):
        """
        Basic information about the file, such as size and file path.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see
                [examples projects](https://github.com/deeplime-io/onecode/tree/1.x/examples)).
            value: Path to the output file. Unless absolute, a path is relative to the `outputs`
                folder of the flow currently running.
            label: Typically to be used for display purpose only. If not defined, it
                will default to the `key`.
            tags: Optional meta-data information about the expected file. This information is only
                used when the JSON output attributes are written to the output manifest.
            make_path: True to create the directory structure of the given file path.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import file_output, Mode, Project

            Project().mode = Mode.EXECUTE
            Project().current_flow = 'test'

            file = file_output(
                key="FileOutput",
                value="/path/to/file.txt",
                label="My FileOutput",
                tags=['TXT'],
                make_path=True
            )

            with open(file, 'w') as f:
                f.write('Hello OneCode!')

            print(file)
            ```

            ```py title="Output"
            # create /path/to folders
            "/path/to/file.txt"
            ```

        """
        super().__init__(
            key,
            value,
            label,
            tags=tags,
            mimetype=mimetypes.guess_type(value)[0],
            **kwargs
        )

        if make_path:
            os.makedirs(os.path.dirname(self.value), exist_ok=True)

    @property
    def value(self) -> str:
        """
        Returns:
            The path to the output file: if path are not absolute, then it is considered relative
                to the data output folder. See [Organizing Data][organizing-data]
                for more information.

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
