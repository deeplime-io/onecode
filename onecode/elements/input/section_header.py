# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Any

from ...base.decorator import check_type
from ..input_element import InputElement


class SectionHeader(InputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: str,
        **kwargs: Any
    ):
        """
        A simple header.

        Args:
            key: ID of the element. It must be unique as it is the key used to store data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `streamlit`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            from onecode import section_header, Mode, Project

            Project().mode = Mode.EXECUTE
            widget = section_header(
                value="My SectionHeader"
            )
            ```

            ```py title="Output"
            "OneCode rocks!"
            ```

        """
        super().__init__(
            key,
            value,
            **kwargs
        )

    @property
    def _value_type(self) -> type:
        """
        Get the SectionHeader value type: string `str`.

        """
        return str

    @check_type
    def _validate(
        self,
        value: str
    ) -> None:
        """
        No validation is performed.

        """
        pass
