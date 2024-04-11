# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
from typing import Any, List, Optional

from ...base.decorator import check_type
from ...base.project import Project
from ..output_element import OutputElement


class PyvistaVrmlOutput(OutputElement):
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
        A Pyvista 3D scene using a VRML output.
        See `pyvista.export_vrml()` for more information. See example `PyVistaViz`.

        !!! warning
            Required packages: `pyvista`, `stpyvista`.

        Args:
            key: ID of the element. It must be unique as it is the key used to store data in
                Project(), otherwise it will lead to conflicts at runtime in both execution and
                Streamlit modes. The key will be transformed into snake case and slugified to avoid
                any special character or whitespace. Note that an ID cannot start with `_`. Try to
                choose a key that is meaningful for your context (see
                [examples projects](https://github.com/deeplime-io/onecode/tree/main/examples)).
            value: Path to the output Plotly JSON file which must have a `.json` extension. Unless
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
            import pyvista as pv
            from onecode import pyvista_vrml_output, Mode, Project

            Project().mode = Mode.EXECUTE
            Project().current_flow = 'test'

            vrml_file = pyvista_vrml_output(
                key="PyvistaVrmlOutput",
                value="/path/to/file.vrml",
                label="My PyvistaVrmlOutput",
                tags=['Graph']
            )

            plotter = pv.Plotter(window_size=[600,600])
            mesh = pv.Cube(center=(0,0,0))
            mesh['myscalar'] = mesh.points[:, 2] * mesh.points[:, 0]
            plotter.add_mesh(mesh, scalars='myscalar', cmap='bwr', line_width=1)
            plotter.view_isometric()
            plotter.background_color = 'white'

            plotter.export_vrml(vrml_file)
            print(vrml_file)
            ```

            ```py title="Output"
            "/path/to/file.vrml"
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
            ValueError: if the file does not have a VRML extension `.vrml`.

        """
        _, ext = os.path.splitext(value)
        valid_ext = [
            '.vrml',
        ]

        if ext.lower() not in valid_ext:
            raise ValueError(
                f"[{self.key}] Invalid VRML extension: {ext} (accepted: {', '.join(valid_ext)})"
            )

    @staticmethod
    def imports() -> List[str]:
        """
        Returns:
            Python import statements required by the Streamlit code.

        """
        return [
            "import pyvista as pv",
            "from stpyvista import stpyvista"
        ]

    @staticmethod
    def streamlit() -> str:
        """
        Returns:
            The Streamlit code to show a Pyvista 3D scene loading a VRML as a Pyvista Plotter.

        """
        return """
_scene = pv.Plotter()
_scene.import_vrml(value)
_scene.reset_camera()
stpyvista(_scene, key='{key}')

"""
