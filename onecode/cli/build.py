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
from ..base.enums import ElementType, Mode
from ..base.project import Project
from .utils import process_call_graph


@check_type
def process(calls: List[Dict[str, str]]) -> Dict:
    """
    Evaluate the given calls such as:
    - only `ElementType.INPUT` are considered.
    - result of evaluation is interpreted as (key, value) and aggregated in the final
        dictionnary returned by this function.

    Ensure the proper `Project().mode` is set before calling this function (as it will control
    the evaluation of the code call). This function is typically used for `InputElement` JSON
    extraction. Although the `extract_json()` function directly pipes the calls from the code
    call graph (through `process_call_graph()`), you may input your own code calls (see example
    below).

    Args:
        calls: List of `{"func": <function_name>, "loc": <code_to_eval>}` where `func` is the name
            of the function corresponding to the `InputElement` (i-e its snake case form - see the
            element developer section for more info), and `loc` is the "line of code" to evaluate
            through the Python interpreter.

    Returns:
        A dictionnary containing the results of the code evaluation associated to their key id.

    !!! example
        ```py
        Project().mode = Mode.EXTRACT_ALL

        # processing a single call of Slider element
        process([{"func": "onecode.slider", "loc": "onecode.slider('my_slider', 0.4)"}])
        # => returns the JSON for this parameter, i-e:
        # { kind: Slider, value: 0.4, label: 'my_slider', ... }

        # processing a single call of a custom MyBox element
        process([{"func": "onecode_ext.my_box", "loc": "onecode_ext.my_box('my_box', 'X')"}])
        # => returns the JSON for this parameter, i-e:
        # { kind: MyBox, value: 'X', label: 'my_box', ... }

        # piping the entire call graph of a OneCode Project
        statements = process_call_graph(project_path)
        for v in statements.values():
            p = process(v["calls"])
            # ...

        ```

    """
    params = {}

    for code in calls:
        try:
            t = eval(f"{code['func']}_type")

            # output are skipped
            if t == ElementType.INPUT:
                k, v = eval(f"{code['loc']}")
                params[k] = v

        except Exception as e:
            print(f"=> {code['loc']}")
            print('Error ', e)

    return params


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

    schema = []

    for flow, cg in statements.items():
        p = process(cg["calls"])
        cur_flow = {
            "id": cg["entry_point"],
            "label": flow,
            "items": p
        }

        # refactor dependencies for easier triggering from the UI
        deps = {}
        for key, props in p.items():
            props["dependencies"] = []

            for elt in props["depends_on"]:
                if elt not in deps:
                    deps[elt] = set()
                deps[elt].add(key)

        for elt_from, elt_to in deps.items():
            cur_flow["items"][elt_from]["dependencies"] = list(elt_to)

        schema.append(cur_flow)

    with open(to_file, 'w') as out:
        json.dump(schema, out, indent=4)


def main() -> None:   # pragma: no cover
    """
    ```bash
    usage: onecode-start [-h] [--modules [MODULES [MODULES ...]]] [--verbose]

    Extract OneCode UI schema to JSON file.

    optional arguments:
      -h, --help            show this help message and exit
      --modules [MODULES [MODULES ...]]
                            Optional list of modules to import first
      --verbose             Print verbose information when processing files
    ```

    """
    parser = argparse.ArgumentParser(description='Extract OneCode UI schema to JSON file.')
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
    # globals()['onecode_ext'] = register_ext_module()

    project_path = args.path if args.path is not None else os.getcwd()

    out_filename = args.output_file if args.output_file.endswith('.json') \
        else f'{args.output_file}.json'

    print('\n')
    extract_gui(project_path, out_filename, args.verbose)
