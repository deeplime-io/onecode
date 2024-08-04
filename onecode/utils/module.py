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


@check_type
def get_imported_modules(scripts_folder: str) -> List[str]:
    """
    Get the names of all modules imported by the Python scripts present in the given folder.

    Args:
        scripts_folder: folder containing the python.

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

    return list(cg.output_external_mods().keys() - {'<builtin>'})


@check_type
def _find_version(dist_name: str) -> str:
    """
    Find the version of the distribution package if found.

    Args:
        dist_name: package distribution name (may be different from import name).

    Return:
        The version of the package or None if not found.

    """
    ctx = importlib.metadata.DistributionFinder.Context(name=dist_name)
    candidates = importlib.metadata.Distribution.discover(context=ctx)
    dist = next(iter(candidates), None)

    return dist.version if dist is not None else None


@check_type
def check_modules_in_env(
    modules: List[str]
) -> Dict[str, bool]:
    """
    Checks whether all imported modules are present in the current Python environment.

    Args:
        modules: list of modules to check.

    Returns:
        Modules metadata organized by module names.

    """
    # map import names into distributions names
    # - find_spec() work on import name (will return if module is present, builtin or not)
    # - packages_distributions() is a dictionnary mapping from import name into distribution name
    # => builtins packages are the ones present in the env but not found in the distributions.
    distributions = importlib.metadata.packages_distributions()

    mods = {}
    for m in modules:
        mod_ok = importlib.util.find_spec(m) is not None
        dist_name = distributions.get(m, [m])[0]
        version = _find_version(dist_name)
        builtin = mod_ok and version is None

        mods[m] = {
            "in_env": mod_ok,
            "builtin": builtin,
            "version": version,
            "dist_name": dist_name
        }

    return mods


@check_type
def write_requirements(
    to_file: str,
    scripts_folder: str = os.getcwd(),
    specify_version: bool = False
) -> None:
    """
    Write the guessed required packages as a file.

    !!! note
        The list of modules may not be 100% accurate as it uses heuristics to do so.

    Args:
        to_file: file in which required modules will be output.
        scripts_folder: folder containing the python. Defaults to the working directory.
        specify_version: lock to a specific version when found in current Python environment.

    """
    with open(to_file, 'w') as f:
        modules = check_modules_in_env(
            get_imported_modules(scripts_folder)
        )

        for _, m in modules.items():
            builtin = m.get("builtin")
            version = m.get("version", "")
            req = m.get("dist_name")

            if version is not None and specify_version:
                req = f"{req}=={version}"

            if not builtin:
                f.write(f"{req}\n")
