# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from typing import Any, List, Optional

from ...base.decorator import check_type
from ...base.project import Project
from ..output_element import OutputElement


class CsvOutput(OutputElement):
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
        A CSV table with a label on top.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see
                [examples projects](https://github.com/deeplime-io/onecode/tree/main/examples)).
            value: Path to the output CSV file which must have a `.csv` extension. Unless absolute,
                a path is relative to the `outputs` folder of the flow currently running.
            label: Typically to be used for display purpose only. If not defined, it
                will default to the `key`.
            tags: Optional meta-data information about the expected file. This information is only
                used when the JSON output attributes are written to the output manifest.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import csv_output, Mode, Project

            Project().mode = Mode.CONSOLE
            widget = csv_output(
                key="CsvOutput",
                value="/path/to/file.csv",
                label="My CsvOutput",
                tags=['CSV']
            )
            print(widget)
            ```

            ```py title="Output"
            "/path/to/file.csv"
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
        Raises:
            ValueError: if the file does not have a CSV extension `.csv`.

        """
        _, ext = os.path.splitext(self.value)
        valid_ext = [
            '.csv',
        ]

        if ext.lower() not in valid_ext:
            raise ValueError(
                f"[{self.key}] Invalid CSV extension: {ext} (accepted: {', '.join(valid_ext)})"
            )
