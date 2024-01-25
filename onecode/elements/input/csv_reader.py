# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ...base.decorator import check_type
from ...base.project import Project
from ..input_element import InputElement


class CsvReader(InputElement):
    @check_type
    def __init__(
        self,
        key: str,
        value: Optional[Union[str, List[str]]],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        tags: Optional[List[str]] = None,
        **kwargs: Any
    ):
        """
        A CSV-file reader returning a Pandas DataFrame.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in execution mode.
                The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see examples projects).
            value: Path to the CSV file. CSV file must exists.
            label: Label to display on top of the table.
            count: Specify the number of occurence of the widget. OneCode typically uses it for the
                UI case. Note that if `count` is defined, the expected `value` should always
                be a list, even if the `count` is `1`. `count` can either be a fixed number
                (e.g. `3`) or an expression dependent of other elements (see
                [Using Expressions][using-runtime-expressions-in-elements] for more information).
            optional: Specify whether the value may be None. `optional` can either be a fixed
                boolean (`False` or `True`) or a conditional expression dependent of other elements
                (see [Using Expressions][using-runtime-expressions-in-elements] for more
                information).
            hide_when_disabled: If element is optional, set it to True to hide it from the
                interface, otherwise it will be shown disabled.
            tags: Optional meta-data information about the expected file. This information is only
                used by the `Mode.EXTRACT_ALL` when dumping attributes to JSON.
            **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
                existing attributes or methods name such as `_validate`, `_value`, etc.

        Raises:
            ValueError: if the `key` is empty or starts with `_`.
            AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

        !!! example
            ```py
            import pandas as pd
            from onecode import csv_reader, Mode, Project

            Project().mode = Mode.EXECUTE
            widget = csv_reader(
                key="CsvReader",
                value="/path/to/file.csv",
                label="My CSV Reader",
                tags=['CSV']
            )

            pd.testing.assert_frame_equal(widget, pd.read_csv("/path/to/file.csv"))
            ```

        """
        super().__init__(
            key,
            value,
            label,
            count,
            optional,
            hide_when_disabled,
            tags=tags,
            **kwargs
        )

    @staticmethod
    def metadata(value: str) -> Dict:
        """
        Returns the metadata associated to the given CSV(s).

        Returns:
            A dictionnary metadata for each CSV path provided:
            ```py
            {
                "columns": df.columns.to_list(),
                "stats": df.describe().to_dict()
            }
            ```

        """
        df = pd.read_csv(value, engine='pyarrow')

        meta = {
            "columns": df.columns.to_list(),
            "stats": df.describe().to_dict()
        }

        return meta

    @property
    def _value_type(self) -> type:
        """
        Get the CsvReader value type: Pandas DataFrame `pd.DataFrame`.

        """
        return pd.DataFrame

    @property
    def value(self) -> Optional[pd.DataFrame]:
        """
        Returns:
            The Pandas DataFrame loaded from the provided file path, otherwise None if the
            file does not exists.

        """
        if self._value is not None:
            if type(self._value) is str:
                filepath = Project().get_input_path(self._value)
                return pd.read_csv(filepath, engine='pyarrow') \
                    if os.path.exists(filepath) or filepath.startswith('https://') else None

            elif type(self._value) is list and all(
                type(v) is str for v in self._value
            ):
                return [
                    pd.read_csv(
                        Project().get_input_path(val),
                        engine='pyarrow'
                    ) if os.path.exists(
                        Project().get_input_path(val)
                    ) or filepath.startswith('https://') else None for val in self._value
                ]

        return None

    @check_type
    def _validate(
        self,
        value: pd.DataFrame
    ) -> None:
        """
        Raises:
            ValueError: if the DataFrame is empty.

        """
        if value.empty:
            raise ValueError(f"[{self.key}] Empty dataframe")

    def _json_form(self) -> Dict:
        return {
            "type": "string",
            "format": "data-url"
        }
