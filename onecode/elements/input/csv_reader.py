# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from typing import Any, BinaryIO, Dict, List, Optional, Union

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pv

from ...base.decorator import check_type
from ...base.project import Project
from ..input_element import InputElement

MAX_UNIQUE = 100_000


def _jsonable(value: Any) -> Any:
    """Convert Arrow/Python scalars to JSON-friendly values."""
    if value is None:
        return None
    if hasattr(value, "as_py"):
        try:
            value = value.as_py()
        except Exception:  # noqa: BLE001
            pass
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    return value


def _metadata_from_table(table: pa.Table) -> Dict[str, Any]:
    """Build the expression-evaluator bag (legacy cloud CSV processor shape)."""
    stats: Dict[str, Any] = {
        ".columns": list(table.column_names),
        "__len__()": int(table.num_rows),
    }

    for column in table.column_names:
        column_data = table[column]
        col_key = f".{column}[]"

        if pa.types.is_floating(column_data.type):
            stats[col_key] = {
                "unique()": None,
                "mode()": None,
                "min()": _jsonable(pc.min(column_data)),
                "max()": _jsonable(pc.max(column_data)),
                "mean()": _jsonable(pc.mean(column_data)),
                "count()": _jsonable(pc.count(column_data)),
                "sum()": _jsonable(pc.sum(column_data)),
            }
        elif pa.types.is_integer(column_data.type):
            uniq = None
            most_freq = None
            try:
                counts = pc.value_counts(column_data)
                uniq = pc.unique(column_data).to_pylist()[:MAX_UNIQUE]
                if len(counts) > 0:
                    most_freq = counts[0][0].as_py()
            except Exception:  # noqa: BLE001
                pass
            stats[col_key] = {
                "unique()": [_jsonable(v) for v in uniq] if uniq is not None else None,
                "mode()": _jsonable(most_freq),
                "min()": _jsonable(pc.min(column_data)),
                "max()": _jsonable(pc.max(column_data)),
                "mean()": _jsonable(pc.mean(column_data)),
                "count()": _jsonable(pc.count(column_data)),
                "sum()": _jsonable(pc.sum(column_data)),
            }
        else:
            uniq = None
            most_freq = None
            try:
                counts = pc.value_counts(column_data)
                uniq = pc.unique(column_data).to_pylist()[:MAX_UNIQUE]
                if len(counts) > 0:
                    most_freq = counts[0][0].as_py()
            except Exception:  # noqa: BLE001
                pass
            stats[col_key] = {
                "unique()": list(uniq) if uniq is not None else None,
                "mode()": _jsonable(most_freq),
                "min()": None,
                "max()": None,
                "mean()": None,
                "count()": _jsonable(pc.count(column_data)),
                "sum()": None,
            }

    return stats


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
        sep: Optional[str] = None,
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
            count: Placeholder, ignore until we activate this feature.
            optional: Specify whether the `value` may be None.
            hide_when_disabled: Placeholder, ignore until we activate this feature.
            tags: Optional meta-data information about the expected file. This information is only
                used by the `Mode.EXTRACT_ALL` when dumping attributes to JSON.
            sep: Optional delimiter used to separate values in the CSV file. If not provided,
                the default delimiter "," will be used.
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
                tags=['CSV'],
                sep=","
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
            csv_options={
                "read_options": {},
                "parse_options": {
                    "delimiter": sep
                },
                "convert_options": {},
            },
            **kwargs
        )

    @staticmethod
    def metadata(value: Union[str, BinaryIO], **options: Any) -> Dict:
        """
        Build dynamic-UI / expression-evaluator metadata for a CSV.

        Uses PyArrow (same approach as the legacy cloud CSV processor) so large files
        can be read from a path or a **stream** (e.g. HTTP signed-URL body) without
        loading via Pandas first.

        Returns the evaluator bag shape:

        ```py
        {
            ".columns": ["A", "B"],
            "__len__()": 123,
            ".A[]": {
                "unique()": [...],
                "mode()": ...,
                "min()": ...,
                "max()": ...,
                "mean()": ...,
                "count()": ...,
                "sum()": ...,
            },
            ...
        }
        ```

        Args:
            value: Filesystem path, or a binary file-like / readable stream.
            **options: Optional ``csv_options`` with ``read_options``, ``parse_options``,
                ``convert_options`` (PyArrow CSV option dicts).
        """
        csv_options = options.get("csv_options") or {}
        read_options = dict(csv_options.get("read_options") or {})
        parse_options = dict(csv_options.get("parse_options") or {})
        convert_options = dict(csv_options.get("convert_options") or {})

        # Drop null delimiter so PyArrow uses its default.
        if parse_options.get("delimiter") is None:
            parse_options.pop("delimiter", None)

        table = pv.read_csv(
            value,
            read_options=pv.ReadOptions(**read_options) if read_options else None,
            parse_options=pv.ParseOptions(**parse_options) if parse_options else None,
            convert_options=pv.ConvertOptions(**convert_options) if convert_options else None,
        )
        return _metadata_from_table(table)

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
                return pd.read_csv(
                    filepath,
                    delimiter=self.csv_options["parse_options"]["delimiter"]
                ) if os.path.exists(filepath) or filepath.startswith('https://') else None

            elif type(self._value) is list and all(
                type(v) is str for v in self._value
            ):
                return [
                    pd.read_csv(
                        Project().get_input_path(val),
                        delimiter=self.csv_options["parse_options"]["delimiter"]
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
