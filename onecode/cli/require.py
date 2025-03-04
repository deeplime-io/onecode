# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT
import argparse  # pragma: no cover
import os  # pragma: no cover

from ..utils import write_requirements  # pragma: no cover


def main() -> None:   # pragma: no cover
    """
    ```bash
    usage: onecode-require [-h] [--path PATH] [--specify-version] output_file

    Output guessed required packages into the given requirements txt file

    positional arguments:
      output_file        Path to the output requirements txt file

    options:
      -h, --help         show this help message and exit
      --path PATH        Path to the project root directory if not the current working directory
      --specify-version  Specify the version if package is present in the current Python environment
    ```

    """
    parser = argparse.ArgumentParser(
        description='Output guessed required packages into the given requirements txt file'
    )
    parser.add_argument(
        'output_file',
        help='Path to the output requirements txt file'
    )
    parser.add_argument(
        '--path',
        required=False,
        help='Path to the project root directory if not the current working directory'
    )
    parser.add_argument(
        '--specify-version',
        help='Specify the version if package is present in the current Python environment',
        action='store_true'
    )
    args = parser.parse_args()

    write_requirements(
        args.output_file,
        args.path if args.path is not None else os.getcwd(),
        args.specify_version
    )
