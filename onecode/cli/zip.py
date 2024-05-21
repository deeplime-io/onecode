# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import argparse
import json
import os
import zipfile

from ..base.decorator import check_type
from .utils import get_flows


@check_type
def zip_output(
    project_path: str,
    data_path: str,
    to_file: str,
    compression_level: int,
    verbose: bool = False,
) -> None:
    """
    """

    compression = zipfile.ZIP_STORED if compression_level == 0 else zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(
        to_file,
        "w",
        compression=compression,
        compresslevel=compression_level
    ) as zf:
        for flow in get_flows(project_path):
            print(f"Processing flow {flow['label']}...")

            with open(os.path.join(data_path, "outputs", flow["file"], "MANIFEST.txt")) as f:
                for line in f:
                    output = json.loads(line)

                    output_file = output["value"]
                    arcpath = os.path.join(
                        "data",
                        os.path.relpath(output_file, os.path.join(data_path, "outputs"))
                    )

                    if verbose:
                        print(f"Archiving {output['key']}: {output_file} => {arcpath}")

                    if os.path.exists(output_file):
                        zf.write(
                            output_file,
                            arcname=arcpath
                        )


def main() -> None:    # pragma: no cover
    """
    """

    parser = argparse.ArgumentParser(description='Start the OneCode Project in Interactive Mode.')
    parser.add_argument(
        '--output_file',
        default='data.zip',
        help='Path to the output zip file'
    )
    parser.add_argument(
        '--path',
        required=False,
        help='Path to the project root directory if not the current working directory'
    )
    parser.add_argument(
        '--data',
        required=False,
        help='Path to the data root directory if not the default data directory'
    )
    parser.add_argument(
        '--compression',
        default=6,
        type=int,
        choices=range(10),
        help='Archivr compression level'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print verbose information when processing files'
    )
    args = parser.parse_args()

    project_path = args.path if args.path is not None else os.getcwd()
    data_path = args.data if args.data is not None else os.path.join(project_path, 'data')
    data_path = os.path.abspath(data_path)

    to_file = args.output_file if args.output_file.endswith('.zip') \
        else f'{args.output_file}.zip'

    print('\n')
    zip_output(project_path, data_path, to_file, args.compression, args.verbose)
