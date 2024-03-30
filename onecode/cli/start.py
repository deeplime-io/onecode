# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import argparse
import importlib
import json
import os
from typing import Dict, List

import onecode  # noqa

from ..base.decorator import check_type
from ..base.enums import *  # noqa
from ..base.enums import ElementType, Env, Mode
from ..base.project import Project
from ..cli.extract import process
from ..utils.module import register_ext_module
from .utils import process_call_graph


@check_type
def extract_gui(
    project_path: str,
    to_file: str,
    verbose: bool = False
) -> None:
    """
    Generate the UI JSON format for OneCode Cloud.

    Args:
        project_path: Path to the root of the OneCode project.
        to_file: Path of the output file to dump the JSON to.
        verbose: If True, print out debug information.

    """
    Project().mode = Mode.BUILD_GUI
    statements = process_call_graph(project_path, verbose)

    schema = {
        "title": os.path.basename(project_path),
        "flows": {}
    }

    for flow, cg in statements.items():
        p = process(cg["calls"])
        schema['flows'][flow] = p

        # refactor dependencies for easier triggering from the UI
        deps = {}
        for key, props in p.items():
            for elt in props["dependencies"]:
                if elt not in deps:
                    deps[elt] = set()
                deps[elt].add(key)
            props["dependencies"] = []

        for elt_from, elt_to in deps.items():
            schema["flows"][flow][elt_from]["dependencies"] = list(elt_to)

    with open(to_file, 'w') as out:
        json.dump(schema, out, indent=4)


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
        '--output_file',
        default='app_ui.json',
        help='Path to the output JSON file'
    )
    parser.add_argument(
        '--modules',
        nargs='*',
        default=[],
        help='Optional list of modules to import first'
    )
    parser.add_argument(
        '--path',
        required=False,
        help='Path to the project root directory if not the current working directory'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print verbose information when processing files'
    )
    args = parser.parse_args()

    # optionally load required modules dynamically,
    # typically modules extending OneCode
    for mod in args.modules:
        globals()[mod] = importlib.import_module(mod)

    # register elements from OneCode inline extensions if any
    globals()['onecode_ext'] = register_ext_module()

    project_path = args.path if args.path is not None else os.getcwd()

    out_filename = args.output_file if args.output_file.endswith('.json') \
        else f'{args.output_file}.json'

    print('\n')
    extract_gui(project_path, out_filename, args.verbose)
