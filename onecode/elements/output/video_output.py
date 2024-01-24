# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from typing import Any, List, Optional

from ...base.decorator import check_type
from ...base.project import Project
from ..output_element import OutputElement


class VideoOutput(OutputElement):
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
        An embedded video player

        Args:
            key: ID of the element. It must be unique as it is the key used to story data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see
                [examples projects](https://github.com/deeplime-io/onecode/tree/main/examples)).
            value: Path to the output video file which must have a `.mp4` extension. Unless
                absolute, a path is relative to the `outputs` folder of the flow currently running.
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
            import matplotlib.pyplot as plt
            from onecode import video_output, Mode, Project

            Project().mode = Mode.EXECUTE
            Project().current_flow = 'test'

            video_file = video_output(
                key="VideoOutput",
                value="/path/to/file.mp4",
                label="My VideoOutput",
                tags=['Video']
            )

            # define your animation here, for instance, with matplotlib
            # https://matplotlib.org/stable/api/animation_api.html

            print(video_file)
            ```

            ```py title="Output"
            "/path/to/file.mp4"
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
            ValueError: if the file does not have an video-like extension, i-e: `.mp4`.

        """
        _, ext = os.path.splitext(self.value)
        valid_ext = [
            '.mp4'
        ]

        if ext.lower() not in valid_ext:
            raise ValueError(
                f"[{self.key}] Invalid video extension: {ext} (accepted: {', '.join(valid_ext)})"
            )

    @staticmethod
    def streamlit() -> str:
        """
        Returns:
            The Streamlit code to show an embedded video player.

        """
        return "st.video(value)"