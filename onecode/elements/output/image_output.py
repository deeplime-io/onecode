# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from typing import Any, List, Optional

from ...base.decorator import check_type
from ...base.project import Project
from ..output_element import OutputElement


class ImageOutput(OutputElement):
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
        An image as part of the image carousel.

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see
                [examples projects](https://github.com/deeplime-io/onecode/tree/main/examples)).
            value: Path to the output image file which must have a `.jpg`, `.jpeg`, `.png` or `.svg`
                extension. Unless absolute, a path is relative to the `outputs` folder of the flow
                currently running.
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
            from onecode import image_output, Mode, Project

            Project().mode = Mode.CONSOLE
            widget = image_output(
                key="ImageOutput",
                value="/path/to/file.jpg",
                label="My ImageOutput",
                tags=['Image']
            )
            print(widget)
            ```

            ```py title="Output"
            "/path/to/file.jpg"
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
            ValueError: if the file does not have an image-like extension, i-e: `.jpg`, `.jpeg`,
                `.png`, `.svg`.

        """
        _, ext = os.path.splitext(self.value)
        valid_ext = [
            '.jpg',
            '.jpeg',
            '.png',
            '.svg',
        ]

        if ext.lower() not in valid_ext:
            raise ValueError(
                f"[{self.key}] Invalid image extension: {ext} (accepted: {', '.join(valid_ext)})"
            )

    @staticmethod
    def streamlit() -> str:
        """
        Returns:
            The Streamlit code to show an image as part of the image carousel.

        !!! tip
            A static function `_show_img(filepath: str)` is available for any Streamlit code to use.
            It will automatically add the given image to the carousel without you needing to deal
            with the carousel.

        """
        return "_show_img(value)"
