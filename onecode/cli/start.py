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
from ..utils.module import register_ext_module
from .utils import process_call_graph


@check_type
def process(calls: List[Dict[str, str]]) -> Dict:
    """

    """
    params = {}
    data = {}
    required = []

    for code in calls:
        try:
            t = eval(f"{code['func']}_type")

            # output are skipped
            if t == ElementType.INPUT:
                k, v = eval(f"{code['loc']}")
                params[k] = v["properties"]
                data[k] = v["value"]
                if not v["optional"]:
                    required.append(k)

        except Exception as e:
            print(f"=> {code['loc']}")
            print('Error ', e)

    return params, data, required


@check_type
def extract_gui(verbose: bool = False) -> None:
    """

    """
    cur_dir = os.getcwd()
    statements = process_call_graph(cur_dir, verbose)

    schema = {
        "title": os.path.basename(cur_dir),
        "type": "object",
        "properties": {}
    }

    data = {}

    for k, v in statements.items():
        _params, _data, _required = process(v["calls"])

        if k in _params.keys():
            raise ValueError(
                f"Step cannot carry the same name as a parameter {k}"
            )

        schema["properties"][k] = {
            "type": "object",
            "title": k,
            "required": _required,
            "properties": _params
        }

        data = {**data, **_data}

        # refactor dependencies for easier triggering from the UI
        deps = {}
        for key, props in _params.items():
            for elt in props["dependencies"]:
                if elt not in deps:
                    deps[elt] = set()
                deps[elt].add(key)
            props["dependencies"] = []

        for elt_from, elt_to in deps.items():
            schema["properties"][k]["properties"][elt_from]["dependencies"] = list(elt_to)

    with open('app_schema.json', 'w') as out_schema:
        json.dump(schema, out_schema, indent=4)

    with open('app_data.json', 'w') as out_data:
        json.dump(data, out_data, indent=4)

    with open('app_ui.json', 'w') as out_ui:
        json.dump({}, out_ui, indent=4)


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

    Project().mode = Mode.BUILD_GUI
    extract_gui(args.verbose)
