# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT
import argparse
import os

from ..base.logger import Logger
from ..utils import check_modules_in_env, get_imported_modules


def main() -> None:   # pragma: no cover
    """
    ```bash
    usage: onecode-check [-h] [--path PATH]

    Check whether all packages are present in the current Python environment

    options:
      -h, --help   show this help message and exit
      --path PATH  Path to the project root directory if not the current working directory
    ```

    """
    parser = argparse.ArgumentParser(
        description='Check whether all packages are present in the current Python environment'
    )
    parser.add_argument(
        '--path',
        required=False,
        help='Path to the project root directory if not the current working directory'
    )
    args = parser.parse_args()

    modules = check_modules_in_env(
        get_imported_modules(args.path if args.path is not None else os.getcwd())
    )

    modules_names = list(modules.keys())
    modules_names = sorted(modules_names)

    for name in modules_names:
        m = modules.get(name)
        in_env = m.get("in_env")
        version = m.get("version", "")
        dist_name = m.get("dist_name")

        if name != dist_name:
            dist_name = f"{name} [{dist_name}]"

        if not in_env:
            Logger.warning(f'💥 {dist_name}')

        else:
            version_str = f" ({version})" if version is not None else ""
            Logger.info(f'✅ {dist_name}{version_str}')
