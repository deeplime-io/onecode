# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

# pyi required for VSCode instrospection
from typing import Any, List, Optional, Tuple, Union

def checkbox(
    key: str,
    value: Optional[Union[bool, List[bool]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    **kwargs: Any
):
    """
    A simple checkbox with a label. Value is either True, False or None.

    Args:
        key: ID of the element. It must be unique as it is the key used to story data in
            Project(), otherwise it will lead to conflicts at runtime in execution mode.
            The key will be transformed into snake case and slugified to avoid
            any special character or whitespace. Note that an ID cannot start with `_`. Try to
            choose a key that is meaningful for your context (see examples projects).
        value: Initial check status: True, False or None.
        label: Label to display next to the checkbox.
        count: Placeholder, ignore until we activate this feature.
        optional: Specify whether the `value` may be None.
        hide_when_disabled: Placeholder, ignore until we activate this feature.
        **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
            existing attributes or methods name such as `_validate`, `_value`, etc.

    Raises:
        ValueError: if the `key` is empty or starts with `_`.
        AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

    !!! example
        ```py
        from onecode import checkbox, Mode, Project

        Project().mode = Mode.EXECUTE
        widget = checkbox(
            key="Checkbox",
            value=True,
            label="My Checkbox"
        )
        print(widget)
        ```

        ```py title="Output"
        True
        ```

    """


def csv_reader(
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
    

def dropdown(
    key: str,
    value: Optional[Union[str, List[str], List[List[str]]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    options: Union[List, str] = [],
    multiple: bool = False,
    **kwargs: Any
):
    """
    A single or multipe choice dropdown menu.

    Args:
        key: ID of the element. It must be unique as it is the key used to story data in
            Project(), otherwise it will lead to conflicts at runtime in execution mode.
            The key will be transformed into snake case and slugified to avoid
            any special character or whitespace. Note that an ID cannot start with `_`. Try to
            choose a key that is meaningful for your context (see examples projects).
        value: Pre-selected value(s) among the options.
        label: Label to display left of the dropdown menu.
        count: Placeholder, ignore until we activate this feature.
        optional: Specify whether the `value` may be None.
        hide_when_disabled: Placeholder, ignore until we activate this feature.
        options: List all possible options available in the dropdown menu.
        multiple: Set to True if multiple choice is allowed, otherwise only a single element can
            be selected.
        **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
            existing attributes or methods name such as `_validate`, `_value`, etc.


    Raises:
        ValueError: if the `key` is empty or starts with `_`.
        AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

    !!! example
        Fixed options:
        ```py
        from onecode import dropdown, Mode, Project

        Project().mode = Mode.EXECUTE
        widget = dropdown(
            key="Dropdown",
            value=["A", "C"],
            options=["A", "B", "C"],
            multiple=True
        )
        print(widget)
        ```

        ```py title="Output"
        ["A", "C"]
        ```

        Dynamic options:
        ```
        from onecode import csv_reader, dropdown, Mode, Project

        Project().mode = Mode.EXECUTE

        df = csv_reader("csv", "/path/to/file.csv")

        widget = dropdown(
            key="Dynamic Dropdown",
            value=None,
            options='$csv$.columns',
            optional=True
        )
        print(widget)
        ```

        ```py title="Output"
        None
        ```

    """


def file_input(
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


def number_input(
    key: str,
    value: Optional[Union[float, List[float]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    min: float = None,
    max: float = None,
    step: float = None,
    **kwargs: Any
):
    """
    A field for numerical values.

    Args:
        key: ID of the element. It must be unique as it is the key used to story data in
            Project(), otherwise it will lead to conflicts at runtime in execution mode.
            The key will be transformed into snake case and slugified to avoid
            any special character or whitespace. Note that an ID cannot start with `_`. Try to
            choose a key that is meaningful for your context (see examples projects).
        value: Initial numerical value.
        label: Label to display on top of the field.
        count: Placeholder, ignore until we activate this feature.
        optional: Specify whether the `value` may be None.
        hide_when_disabled: Placeholder, ignore until we activate this feature.
        min: Optionally limit the possible values with a lower bound.
        max: Optionally limit the possible values with an upper bound.
        step: Optionally set a step used when increment/decrement button are used.
        **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
            existing attributes or methods name such as `_validate`, `_value`, etc.

    Raises:
        ValueError: if the `key` is empty or starts with `_`.
        AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

    !!! example
        ```py
        from onecode import number_input, Mode, Project

        Project().mode = Mode.EXECUTE
        widget = number_input(
            key="Number Input",
            value=5.1,
            min=5,
            max=6
        )
        print(widget)
        ```

        ```py title="Output"
        5.1
        ```

    """


def radio_button(
    key: str,
    value: Optional[Union[str, List[str]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    options: List[str] = [],
    horizontal: bool = False,
    **kwargs: Any
):
    """
    A single choice represented as a group of exclusive radio buttons.

    Args:
        key: ID of the element. It must be unique as it is the key used to story data in
            Project(), otherwise it will lead to conflicts at runtime in execution mode.
            The key will be transformed into snake case and slugified to avoid
            any special character or whitespace. Note that an ID cannot start with `_`. Try to
            choose a key that is meaningful for your context (see examples projects).
        value: Radio button initially selected.
        label: Label to display on top of the field.
        count: Placeholder, ignore until we activate this feature.
        optional: Specify whether the `value` may be None.
        hide_when_disabled: Placeholder, ignore until we activate this feature.
        options: List all possible options available.
        horizontal: Set to True to have radio buttons displayed horizontally, otherwise radio
            buttons will be displayed vertically.
        **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
            existing attributes or methods name such as `_validate`, `_value`, etc.

    Raises:
        ValueError: if the `key` is empty or starts with `_`.
        AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

    !!! example
        Fixed options:
        ```py
        from onecode import radio_button, Mode, Project

        Project().mode = Mode.EXECUTE
        widget = radio_button(
            key="RadioButton",
            value="A",
            options=["A", "B", "C"]
        )
        print(widget)
        ```

        ```py title="Output"
        "A"
        ```

        Dynamic options:
        ```
        from onecode import csv_reader, radio_button, Mode, Project

        Project().mode = Mode.EXECUTE

        df = csv_reader("csv", "/path/to/file.csv")

        widget = radio_button(
            key="Dynamic RadioButton",
            value=None,
            options='$csv$.columns',
            optional=True
        )

        assert widget is None
        ```

    """


def slider(
    key: str,
    value: Optional[Union[float, List[float]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    min: float = 0.,
    max: float = 1.,
    step: float = 0.1,
    **kwargs: Any
):
    """
    A slider for numerical values.

    Args:
        key: ID of the element. It must be unique as it is the key used to story data in
            Project(), otherwise it will lead to conflicts at runtime in execution mode.
            The key will be transformed into snake case and slugified to avoid
            any special character or whitespace. Note that an ID cannot start with `_`. Try to
            choose a key that is meaningful for your context (see examples projects).
        value: Initial numerical value.
        label: Label to display on top of the field.
        count: Placeholder, ignore until we activate this feature.
        optional: Specify whether the `value` may be None.
        hide_when_disabled: Placeholder, ignore until we activate this feature.
        min: Mandatory lower bound, defaults to 0.
        max: Mandatory upper bound, defaults to 1.
        step: Mandatory step used when incrementing/decrementing the slider, defaults to 0.1.
        **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
            existing attributes or methods name such as `_validate`, `_value`, etc.

    Raises:
        ValueError: if the `key` is empty or starts with `_`.
        AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

    !!! example
        ```py
        from onecode import slider, Mode, Project

        Project().mode = Mode.EXECUTE
        widget = slider(
            key="Slider",
            value=5.1,
            min=5,
            max=6
        )
        print(widget)
        ```

        ```py title="Output"
        5.1
        ```

    """


def text_input(
    key: str,
    value: Optional[Union[str, List[str]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    max_chars: int = None,
    placeholder: str = None,
    **kwargs: Any
):
    """
    A simple text field.

    Args:
        key: ID of the element. It must be unique as it is the key used to story data in
            Project(), otherwise it will lead to conflicts at runtime in execution mode.
            The key will be transformed into snake case and slugified to avoid
            any special character or whitespace. Note that an ID cannot start with `_`. Try to
            choose a key that is meaningful for your context (see examples projects).
        value: Initial text value.
        label: Label to display on top of the text area.
        count: Placeholder, ignore until we activate this feature.
        optional: Specify whether the `value` may be None.
        hide_when_disabled: Placeholder, ignore until we activate this feature.
        max_chars: Maximum number of characters allowed for this text field.
        placeholder: Placeholder text shown whenever there is no value.
        multiline: Set to True or a height in pixels to make it multiline text area.
        **kwargs: Extra user meta-data to attach to the element. Argument names cannot overwrite
            existing attributes or methods name such as `_validate`, `_value`, etc.

    Raises:
        ValueError: if the `key` is empty or starts with `_`.
        AttributeError: if one the `kwargs` conflicts with an existing attribute or method.

    !!! example
        ```py
        from onecode import text_input, Mode, Project

        Project().mode = Mode.EXECUTE
        widget = text_input(
            key="TextInput",
            value="OneCode rocks!",
            label="My TextInput"
        )
        print(widget)
        ```

        ```py title="Output"
        "OneCode rocks!"
        ```

    """
