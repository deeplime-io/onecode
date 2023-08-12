# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import argparse
import importlib
import os

import onecode  # noqa

from ..base.enums import *  # noqa
from ..base.enums import Env, Mode
from ..base.project import Project
from ..utils.module import register_ext_module


def main() -> None:   # pragma: no cover
    """
    ```bash
    usage: onecode-start [-h] [--modules [MODULES [MODULES ...]]] [--verbose]

    Start the OneCode Project in Interactive mode.

    optional arguments:
      -h, --help            show this help message and exit
      --modules [MODULES [MODULES ...]]
                            Optional list of modules to import first
      --verbose             Print verbose information when processing files
    ```

    """
    parser = argparse.ArgumentParser(description='Start the OneCode Project in Interactive Mode.')
    parser.add_argument(
        '--modules',
        nargs='*',
        default=[],
        help='Optional list of modules to import first'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print verbose information when processing files'
    )
    args = parser.parse_args()

    # if data root not set, set it to data folder in current working directory
    if Env.ONECODE_PROJECT_DATA not in os.environ:
        os.environ[Env.ONECODE_PROJECT_DATA] = os.path.join(os.getcwd(), 'data')
        Project().reset()

    # optionally load required modules dynamically,
    # typically modules extending OneCode
    for mod in args.modules:
        globals()[mod] = importlib.import_module(mod)

    # register elements from OneCode inline extensions if any
    globals()['onecode_ext'] = register_ext_module()

    Project().mode = Mode.EXECUTE
    print("Coming soon...")
