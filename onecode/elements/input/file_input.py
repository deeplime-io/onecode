# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
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
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Path to file(s). Files' existence will be checked at execution time. If paths
                are not absolute, then they are considered relative to the data root folder. See
                [Organizing Data][organizing-data] for more information.
            label: Label to display left of the file selector.
            count: Placeholder, ignore until we activate this feature.
            optional: Specify whether the `value` may be None.
            hide_when_disabled: Placeholder, ignore until we activate this feature.
            types: List of filters allowing to narrow file selection in the UI mode. Each filter
                must be a pair of (name, list of allowed extensions), e.g.
                `("Image", ".jpg .png .jpeg")`. You may use the FileFilter enums for convenience.
            multiple: Set to True if multiple choice is allowed, otherwise only a single element can
                be selected.
            tags: Optional meta-data information about the expected file. This information is only
                used by the `Mode.EXTRACT_ALL` when dumping attributes to JSON.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.

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
                [Organizing Data][organizing-data] for more information.

        """
        if self._value is not None:
            if is_type(self._value, self._value_type):
                return [Project().get_input_path(f) for f in self._value] if self.multiple \
                    else Project().get_input_path(self._value)

            elif type(self._value) is list and all(
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
