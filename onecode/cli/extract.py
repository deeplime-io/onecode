# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import argparse
import importlib
import json
import os
from typing import Dict, List, Optional

from yaspin import yaspin

import onecode  # noqa

from ..base.decorator import check_type
from ..base.enums import *  # noqa
from ..base.enums import ElementType, Mode
from ..base.project import Project
from ..utils.module import register_ext_module
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
def extract_json(
    project_path: str,
    to_file: str,
    all: Optional[bool] = False,
    verbose: bool = False
) -> None:
    """
    Extract the input parameter out of the given OneCode project and dump it to the specified file.

    Args:
        project_path: Path to the root of the OneCode project.
        to_file: Path of the output file to dump the JSON to.
        all: If False, extract only the values of the parameter, otherwise extract values and
            associated data such as `label`, `kind`, etc.
        verbose: If True, print out debug information.

    """
    Project().mode = Mode.EXTRACT_ALL if all else Mode.EXTRACT
    statements = process_call_graph(project_path, verbose)

    parameters = {}
    for v in statements.values():
        p = process(v["calls"])
        parameters = {**parameters, **p}

    with open(to_file, 'w') as out:
        json.dump(parameters, out, indent=4)


@check_type
def main(cli: bool = True) -> None:    # pragma: no cover
    """
    ```bash
    usage: onecode-extract [-h] [--all] [--modules [MODULES [MODULES ...]]] [--path PATH]
        [--verbose] output_file

    Extract OneCode project parameters to JSON file

    positional arguments:
      output_file           Path to the output JSON file

    optional arguments:
      -h, --help            Show this help message and exit
      --all                 Extract parameters with their full info set
      --modules [MODULES [MODULES ...]]
                            Optional list of modules to import first
      --path PATH           Path to the project root directory if not the current working directory
      --verbose             Print verbose information when processing files
    ```

    """
    parser = argparse.ArgumentParser(
        description='Extract OneCode project parameters to JSON file'
    )
    parser.add_argument(
        'output_file',
        help='Path to the output JSON file'
    )
    parser.add_argument(
        '--all',
        help='Extract parameters with their full info set',
        action='store_true'
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
        help='Print verbose information when processing files',
        action='store_true'
    )
    args = parser.parse_args()

    with yaspin(text="Extracting parameters") as spinner:
        try:
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
            extract_json(project_path, out_filename, args.all, args.verbose)

            spinner.text = f"Parameters extracted to {out_filename}"
            spinner.ok("✅")

        except Exception as e:
            spinner.text = f"{e}"
            spinner.fail("💥 [Failed] -")

            if not cli:
                raise e
