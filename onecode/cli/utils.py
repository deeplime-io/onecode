# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import ast
import json
import os
from collections import OrderedDict
from glob import iglob
from typing import Dict, List, Optional

import pydash
from astunparse import unparse
from InquirerPy.base.control import Choice
from pycg.pycg import CallGraphGenerator
from pycg.utils.constants import CALL_GRAPH_OP
from slugify import slugify

from ..base.decorator import check_type
from ..base.enums import Env
from ..base.project import Project


@check_type
def get_flows(project_path: str) -> Dict:
    """
    Get the flows configuration as stored at the OneCode project's root (filename is given by the
    variable `Env.ONECODE_CONFIG_FILE`).

    Args:
        project_path: Path to the root of the OneCode project.

    Returns:
        The JSON content of the OneCode project flow configuration as a dictionnary.

    """
    config_file = os.path.join(project_path, Env.ONECODE_CONFIG_FILE)
    config = []
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)

    return config


@check_type
def _get_flow_choices(project_path: str) -> List[Choice]:     # pragma: no cover
    """
    Internal function for CLI commands to get the existing OneCode project's flows as interactive
    Choice for InquirerPy.

    Args:
        project_path: Path to the root of the OneCode project.

    Returns:
        Flow id and label as InquirerPy Choices.

    """
    flows = get_flows(project_path)
    choices = [Choice(value=gf['file'], name=gf['label']) for gf in flows]
    choices.append(Choice(value=None, name="Put at the end"))
    return choices


@check_type
def _add_flow(
    project_path: str,
    name: Optional[str],
    before: Optional[str] = None
) -> None:
    """
    Internal function to add a flow to an existing OneCode project.

    Args:
        project_path: Path to the root of the OneCode project.
        name: Name of the new flow to add. Note that the name will be slugified, i-e all special
            characters and whitespaces will be converted to "_". See `slugify` for more information.
        before: Insert the new flow before this flow id. Set it to None to put it in last position.

    Raises:
        ValueError: if the flow name is empty or is already used.

    """
    # check names are provided
    if not name:
        raise ValueError("Empty flow name")

    runner_name = slugify(name, separator='_')

    # get content of existing config file if any
    config_file = os.path.join(project_path, Env.ONECODE_CONFIG_FILE)
    flows = get_flows(project_path)

    # ensure flow doesn't already exist
    if pydash.find(flows, lambda x: x['file'] == runner_name) is not None:
        raise ValueError(f'Flow {name} is already registered, please pick another name')

    # insert flow before a given one or append to end of the flows
    idx = pydash.find_index(flows, lambda x: x['file'] == before)
    if idx < 0:
        idx = len(flows)
    pydash.splice(flows, idx, 0, {"file": runner_name, "label": name, "attributes": {}})

    # write out the runner template
    with open(os.path.join(project_path, 'flows', f'{runner_name}.py'), 'w') as f:
        f.write(f"""
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('{runner_name}.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

import onecode


def run():
    onecode.Logger.info(
        \"""
        #####################################################################
        ###> Hello from {name}!
        ###> Fill in this run() function with something awesome!
        #####################################################################
        \"""
    )
""")

    # write out the new config
    with open(config_file, 'w') as f:
        json.dump(flows, f, indent=4)


# check_type decorator not compatible with recursive calls
def extract_calls(
    entry_point: str,
    graph: Dict,
    calls: List[Dict[str, str]],
    verbose: bool = False
) -> None:
    """
    Given a code Call Graph, extract only the code calls related to OneCode-like elements. This
    includes built-in input/output elements from OneCode and also any registered element coming from
    `onecode_ext` as well as derived OneCode packages.

    Args:
        entry_point: Call Graph function name from which to start the extraction from, e.g.
            `flows.my_flow.run`.
        graph: Call Graph typically constructed by the DeepLime forked PyCG. Check out PyCG for
            more information about the graph structure or directly the forked repository at
            https://github.com/deeplime-io/PyCG/tree/onecode
        calls: List of calls as `{"func": <function_name>, "loc": <code_to_eval>}` where results
            are aggregated. These `calls` are typically piped to the `process` functions for JSON
            extraction.
        verbose: If True, print out debug information such as elements being processed.

    """
    # Elements are registered using class name, e.g.: onecode.TextInput
    # However here we are dealing with their snake case counterpart, e.g.: onecode.text_input
    # So we need to snake case the 2nd part of it (the 1st part may not necessarily be snake case)
    registered_elements = {
        f"{ent.split('.')[0]}.{pydash.snake_case(ent.split('.')[1])}"
        for ent in Project().registered_elements
    }

    # PyCG is not exactly equivalent on Windows vs Linux wrt to graph keys
    if os.name == 'nt' and not entry_point.startswith('flows\\'):
        entry_point = f'flows\\{entry_point}'

    if entry_point in graph:
        for fn in graph[entry_point]:
            if fn['normed'] in registered_elements:
                if verbose:
                    print(f" >> ({entry_point}) function {fn['normed']} ✅")

                # replace original function name with normed name
                code = ast.parse(fn['code'])
                code.body[0].value.func = ast.parse(fn['normed'])
                calls.append({
                    "func": fn['normed'],
                    "loc": unparse(code).strip()
                })
            else:
                if verbose:
                    print(f" >> ({entry_point}) function {fn['normed']} ⏩")

                extract_calls(fn['normed'], graph, calls)


@check_type
def process_call_graph(
    project_path: str = None,
    verbose: bool = False
) -> OrderedDict:
    """
    Process a OneCode project to extract the code calls related to OneCode-like elements.

    Args:
        project_path: Path to the root of the OneCode project.
        verbose: If True, print out debug information such as elements being processed.

    Raises:
        FileNotFoundError: if the OneCode project configuration file is not found.

    Returns:
        The list of OneCode-like elements code statements ready to be evaluated.

    """
    if project_path is None:
        project_path = os.getcwd()
    else:
        project_path = os.path.abspath(project_path)

    if not os.path.isfile(os.path.join(project_path, Env.ONECODE_CONFIG_FILE)):
        raise FileNotFoundError('Ensure you are at the root of your OneCode project')

    statements = OrderedDict()
    entry_files = [
        filename for filename in iglob(
            os.path.join(project_path, 'flows', '**', '*.py'), recursive=True
        ) if filename != '__init__.py' and not filename.startswith(
            os.path.join(project_path, 'flows', 'onecode_ext')
        )
    ]

    cg = CallGraphGenerator(
        entry_files,
        project_path,
        -1,
        CALL_GRAPH_OP
    )
    cg.analyze()
    flow_graph = cg.output_enriched()

    for flow in get_flows(project_path):
        label = flow["label"]
        file = flow['file']

        print(f"Processing {label}...")

        calls = []
        if os.name == 'nt':
            extract_calls(f"{file}.run", flow_graph, calls, verbose)
        else:
            extract_calls(f"flows.{file}.run", flow_graph, calls, verbose)

        statements[label] = {
            "entry_point": file,
            "calls": calls
        }

    return statements
