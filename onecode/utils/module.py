# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import importlib
import os
import sys
from glob import iglob
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional

from pycg.pycg import CallGraphGenerator
from pycg.utils.constants import CALL_GRAPH_OP

from ..base.decorator import check_type
from ..base.logger import Logger


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


def get_imported_modules(scripts_folder: str = os.getcwd()) -> List[str]:
    """
    Get the names of all modules imported by the Python scripts present in the given folder.

    Args:
        scripts_folder: folder containing the python. Defaults to the working directory.

    Returns:
        List of modules names imported by the Python scripts.

    """
    entry_files = list(iglob(os.path.join(scripts_folder, '**', '*.py'), recursive=True))
    cg = CallGraphGenerator(
        entry_files,
        scripts_folder,
        0,
        CALL_GRAPH_OP
    )
    cg.analyze()

    return list(cg.output_external_mods().keys())


def check_modules_in_env(
    modules: List[str],
    verbose: bool = False
) -> Dict[str, bool]:
    """
    Check whether all imported modules are present in

    !!! info
        It is not required to call this function explicitely. It is already done automatically as
        part of the OneCode project under `main.py`.

    Args:
        scripts_folder: Path to the root of the OneCode project.

    Returns:
        The module if it contains Python code, otherwise None.

    """
    mods = {}
    for m in modules:
        mod_ok = importlib.util.find_spec(m) is not None or m == '<builtin>'
        mods[m] = mod_ok
        if verbose:
            if mod_ok:
                Logger.info(f'{m} ✅')
            else:
                Logger.warning(f'{m} 💥')

    return mods
