# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT
import argparse  # pragma: no cover
import os  # pragma: no cover

from ..base.logger import Logger  # pragma: no cover
from ..utils import check_modules, get_imported_modules  # pragma: no cover


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

    project_path = args.path if args.path is not None else os.getcwd()
    modules = check_modules(
        modules=get_imported_modules(project_path),
        requirements_file=os.path.join(project_path, 'requirements.txt')
    )

    for name, m in modules.items():
        msg = m.get("msg")

        if msg is not None:
            Logger.warning(msg)
        else:
            dist_name = m.get("dist_name")
            version = m.get("version")
            version_str = f" ({version})" if version is not None else ""

            if name != dist_name:
                dist_name = f"{name} [{dist_name}]"

            Logger.info(f'✅ {dist_name}{version_str}')
