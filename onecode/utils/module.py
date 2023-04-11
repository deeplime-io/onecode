# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import importlib
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional

from ..base.decorator import check_type


@check_type
def register_ext_module(
    project_path: str = os.getcwd(),
    module_name: str = "onecode_ext",
) -> Optional[ModuleType]:
    """
    Register the OneCode Extension module with the specified module name: it must match the folder
    name located in the `flows` directory of the OneCode project.

    Note that a `onecode_ext` module is shipped by default with any OneCode project. As soon as the
    developer creates new elements as part of this module, the `onecode_ext` will be registered.
    See [Extending OneCode][extending-onecode] for more information.

    !!! info
        It is not required to call this function explicitely. It is already done automatically as
        part of the OneCode project under `main.py`.

    Args:
        project_path: Path to the root of the OneCode project.

    Returns:
        The module if it contains Python code, otherwise None.

    """
    code_ext_path = os.path.join(project_path, 'flows', module_name)
    py_files = [f for f in Path(code_ext_path).rglob("*.[pP][yY]") if f.name != '__init__.py']

    if len(py_files) > 0:
        spec = importlib.util.spec_from_file_location(
            module_name,
            os.path.join(code_ext_path, "__init__.py")
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        return module
