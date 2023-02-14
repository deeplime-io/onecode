# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import argparse
import importlib
import os
from typing import Dict, List, Optional

import toml
import yourcode  # noqa

import onecode  # noqa
from onecode import ElementType, Env, Mode, Project, register_ext_module
from onecode.cli.extract import process_call_graph


def process(calls: List[Dict[str, str]]) -> Dict:
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


def extract_toml(
    project_path: str,
    to_file: str,
    all: Optional[bool] = False
) -> None:
    Project().mode = Mode.EXTRACT_ALL if all else Mode.EXTRACT
    statements = process_call_graph(project_path)

    parameters = {}
    for v in statements.values():
        p = process(v["calls"])
        parameters = {**parameters, **p}

    with open(to_file, 'w') as out:
        toml.dump(parameters, out, encoder=toml.TomlNumpyEncoder())


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Extract OneCode project parameters to TOML file'
    )
    parser.add_argument('output_file', help='Path to the output TOML file')
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
    args = parser.parse_args()

    # optionally load required modules dynamically,
    # typically modules extending OneCode
    for mod in args.modules:
        globals()[mod] = importlib.import_module(mod)

    # register elements from OneCode inline extensions if any
    globals()['onecode_ext'] = register_ext_module()

    project_path = args.path if args.path is not None else os.getcwd()

    out_filename = args.output_file if args.output_file.endswith('.toml') \
        else f'{args.output_file}.toml'

    extract_toml(project_path, out_filename, args.all)

    print(f"Parameters extracted to {out_filename}")
