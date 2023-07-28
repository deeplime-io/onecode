# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import argparse
import importlib
import os
import sys
from typing import Dict, List, Set, Tuple

from streamlit.web.cli import main_run

import onecode  # noqa

from ..base.decorator import check_type
from ..base.enums import *  # noqa
from ..base.enums import ElementType, Env, Keyword, Mode
from ..base.project import Project
from ..utils.format import indent_block
from ..utils.module import register_ext_module
from .utils import process_call_graph


@check_type
def process(calls: List[Dict[str, str]]) -> Tuple[List[str], List[str]]:
    """
    Evaluate the given calls such as:
    - result of evaluation is interpreted as a code block.
    - resulting code block is appended to the list of their corresponding element type
        (i-e input code block list for `InputElement` and output code block list for
        `OutputElement`).

    Ensure the proper `Project().mode` is set before calling this function (as it will control
    the evaluation of the code call). This function is typically used for Streamlit code generation.
    Although the `prepare_streamlit_file()` function directly pipes the calls from the code
    call graph (through `process_call_graph()`), you may input your own code calls (see example
    below).

    Args:
        calls: List of `{"func": <function_name>, "loc": <code_to_eval>}` where `func` is the name
            of the function corresponding to the `InputElement` (i-e its snake case form - see the
            element developer section for more info), and `loc` is the "line of code" to evaluate
            through the Python interpreter.

    Returns:
        The pair of two lists: one containing the code evaluation for the `InputElement` and one
        containing the code evaluation for the `OutputElement`.

    !!! example
        ```py
        Project().mode = Mode.STREAMLIT

        # processing a single call of Slider element
        process([{"func": "onecode.slider", "loc": "onecode.slider('My Slider', 0.4)"}])
        # => returns the streamlit code for this parameter, i-e:
        # Slider {self.key}
        # my_slider = st.slider(
        #     'My Slider',
        #     min_value=0.,
        #     max_value=1.,
        #     value=0.4,
        #     step=0.1,
        #     disabled=False,
        #     key='my_slider'
        # )

        # piping the entire call graph of a OneCode Project
        statements = process_call_graph(project_path)
        for v in statements.values():
            inputs, outputs = process(v["calls"])
            # ...

        ```

    """
    streamlit_input = []
    streamlit_output = set()

    for code in calls:
        try:
            t = eval(f"{code['func']}_type")

            if t == ElementType.INPUT:
                c = eval(f"{code['loc']}")
                streamlit_input.append(c)

            elif t == ElementType.OUTPUT:
                c = eval(f"{code['func']}()")
                streamlit_output.add(c)

        except Exception as e:
            print(f"=> {code['loc']}")
            print('Error ', e)

    return streamlit_input, list(streamlit_output)


@check_type
def get_import_statements(calls: List[Dict[str, str]]) -> Tuple[Set[str], Set[str]]:
    """
    Get the import and init statements from the elements called.

    Args:
        calls: List of `{"func": <function_name>, "loc": <code_to_eval>}` where `func` is the name
            of the function corresponding to the `InputElement` (i-e its snake case form - see the
            element developer section for more info), and `loc` is the "line of code" to evaluate
            through the Python interpreter.

    Returns:
        The pair of two sets containing respectively imports statements and init statements.

    !!! example
        ```py
        # getting statements from a single call of FileInput element
        get_import_statements(
            [{"func": "onecode.file_input", "loc": "onecode.file_input('file', 'a.txt')"}]
        )
        ```

        ```py title="Output"
        {"import tkinter as tk", "from tkinter import filedialog"}, {'_root = tk.Tk()\n
        _root.withdraw()\n
        _root.wm_attributes('-topmost', 1)'}
        ```

    """
    imports = set()
    init = set()

    for code in calls:
        try:
            i1 = eval(f"{code['func']}_imports")
            i2 = eval(f"{code['func']}_init")
            imports.update(i1)
            init.add(i2)

        except Exception as e:
            print(f"=> {code['func']}_imports")
            print(f"=> {code['func']}_init")
            print('Error ', e)

    return imports, init


@check_type
def prepare_streamlit_file(
    project_path: str,
    to_file: str,
    verbose: bool = False
) -> None:
    """
    Prepare the Streamlit App Python file from the given OneCode project and dump it to the
    specified file.

    Args:
        project_path: Path to the root of the OneCode project.
        to_file: Path of the output file to dump the Streamlit Python code to.

    """
    Project().mode = Mode.STREAMLIT

    statements = process_call_graph(project_path, verbose)
    menu_entries = statements.keys()

    all_st_outputs = set()
    all_import_libs = set()
    all_init_libs = set()

    for k, v in statements.items():
        imports, init = get_import_statements(v["calls"])
        all_import_libs.update(imports)
        all_init_libs.update(init)

    import_statements = '\n'.join(sorted(all_import_libs))
    init_statements = '\n'.join(sorted(all_init_libs))

    with open(to_file, 'w') as f:
        f.write(f"""###########################################
#    !! THIS FILE IS AUTO-GENERATED !!    #
###########################################

import ast
import json
import logging
import os
import traceback
import uuid
from typing import Dict, List

import pydash
import streamlit as st
from main import main
from streamlit_image_select import image_select
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select

from onecode import ColoredFormatter

# Imports from Elements
{import_statements}

# Init from Elements
{init_statements}

# OneCode init
{Keyword.DATA} = {{}}
_placeholders = {{}}


def _write_logs(id: str) -> None:
    if f'__logs__{{id}}' in st.session_state:
        with _placeholders[id].container():
            st.markdown(
                f'''<div style="
                    background-color:black;
                    padding:1em;
                    margin-bottom:1em;
                    font-family:Source Code Pro, monospace;
                    font-size:0.8em">
                        {{''.join(st.session_state[f'__logs__{{id}}'])}}
                </div>''',
                unsafe_allow_html=True
            )


def _clear_logs(id: str) -> None:
    if f'__logs__{{id}}' in st.session_state:
        st.session_state[f'__logs__{{id}}'] = []
        _write_logs(id)


def _log(
    id: str,
    type: int,
    msg: str
) -> None:
    if id != st.session_state['__current_step_id__']:
        return

    if f'__logs__{{id}}' not in st.session_state:
        st.session_state[f'__logs__{{id}}'] = []

    color = "white"
    if type == logging.DEBUG:
        color="grey"
    elif type == logging.WARNING:
        color = "orange"
    elif type == logging.ERROR or type == logging.CRITICAL:
        color = "red"

    msg = msg.split("\\n")
    st.session_state[f'__logs__{{id}}'].append(
        f'<span style="color:{{color}}">{{"<br />".join(msg)}}</span><br />'
    )
    _write_logs(id)


class _StreamlitLogHandler(logging.Handler):
    def __init__(
        self,
        id: str
    ):
        self._id = id
        logging.Handler.__init__(self)

    def emit(self, record):
        _log(
            self._id,
            record.levelno,
            self.format(record)
        )


def _file_to_tree(
    file_id: str,
    file_relpath: str,
    cur_path: str,
    tree: List[Dict[str, str]]
) -> None:
    path_split = file_relpath.split(os.path.sep, 1)
    path_head = path_split[0]

    if len(path_split) == 1:   # this is a file
        tree.append({{
            "label": path_head,
            "value": file_id,
        }})

    elif not path_head:  # means path starts with leading '/' => ignore
        _file_to_tree(file_id, path_split[1], cur_path, tree)

    else:
        node = pydash.find(tree, {{"label": path_head}})
        cur_path_agg = os.path.sep.join([cur_path, path_head])

        if node is None:
            n = {{
                "label": path_head,
                "value": cur_path_agg,
                "children": []
            }}
            tree.append(n)
            _file_to_tree(file_id, path_split[1], cur_path_agg, n["children"])

        else:
            _file_to_tree(file_id, path_split[1], cur_path_agg, node["children"])


def _show_img(path: str) -> None:
    _id = st.session_state.get('__current_step_id__')

    if not os.path.exists(path) and not os.path.isfile(path):
        st.warning(f'Invalid file path: {{path}}')

    elif _id is not None:
        _imgs = st.session_state.get(f'__selected_images__{{_id}}__', [])
        _imgs.append(path)
        st.session_state[f'__selected_images__{{_id}}__'] = pydash.uniq(_imgs)


with st.sidebar:
    _selected = option_menu("Main Menu", [{', '.join(menu_entries)}])

    # making a button despite this comment
    # https://github.com/streamlit/streamlit/issues/468#issuecomment-807166632
    if st.button('Stop Application'):
        os._exit(0)

""")

        for k, v in statements.items():
            inputs, outputs = process(v["calls"])
            inputs = indent_block(inputs)
            outputs_st = ''
            for out in outputs:
                if out not in all_st_outputs:
                    outputs_st += indent_block(out, indent=0)
                    all_st_outputs.add(out)

            f.write(f"""
{outputs_st}

if _selected == {k}:
    {inputs}
    _step_id = '{v["entry_point"]}'
    st.session_state['__current_step_id__'] = _step_id
    _result = None
    _run_button = st.button('Run')
    with st.expander('Logs', True):
        _placeholders[_step_id] = st.empty()
        _write_logs(_step_id)

    if _run_button:
        with st.spinner('Running...'):
            try:
                _clear_logs(_step_id)
                handler = _StreamlitLogHandler(_step_id)
                handler.setFormatter(ColoredFormatter(False))
                _result =  main({Keyword.DATA}, _step_id, handler)
                st.info('Run finished')

                _nodes = []
                _json_output = []
                if os.path.exists(_result):
                    with open(_result) as f:
                        _json_output = pydash.sort_by(
                            json.loads(f"[{{', '.join([line.rstrip() for line in f])}}]"),
                            'value'
                        )

                    for _out in _json_output:
                        _filepath = _out.get('value')
                        if os.path.exists(_filepath):
                            _relpath = os.path.relpath(_filepath, os.getcwd())
                            _out['_id'] = str(uuid.uuid4())
                            _file_to_tree(_out['_id'], _relpath, '', _nodes)

                st.session_state[f'__nodes__{{_step_id}}__'] = _nodes
                st.session_state[f'__nodes_flat__{{_step_id}}__'] = _json_output

            except Exception as _e:
                st.error(
                    '\\n'.join(
                        traceback.format_exception(
                            etype=type(_e),
                            value=_e,
                            tb=_e.__traceback__
                        )
                    )
                )

    _return_select = tree_select(
        st.session_state.get(f'__nodes__{{_step_id}}__', []),
        expand_on_click=True,
        only_leaf_checkboxes=True,
        show_expand_all=True
    )

    _shown_files = []
    for _sel in _return_select.get('checked'):
        _n = pydash.find(
            st.session_state.get(f'__nodes_flat__{{_step_id}}__', []),
            {{"_id": _sel}}
        )
        if _n is not None:
            _shown_files.append(_n['value'])

            _fname = f"_{{_n['kind']}}"
            if _fname in locals():
                locals()[_fname](**pydash.omit(_n, ['_id']))

    # keep only added images still selected in the tree
    _selected_imgs = st.session_state.get(f'__selected_images__{{_step_id}}__', [])
    _selected_imgs = pydash.intersection(_selected_imgs, _shown_files)
    st.session_state[f'__selected_images__{{_step_id}}__'] = _selected_imgs

    if len(_selected_imgs) > 0:
        _img = image_select(
            label="Select an image",
            images=list(_selected_imgs),
            captions=[os.path.basename(_i) for _i in _selected_imgs],
            use_container_width=False
        )
        if _img is not None:
            # relpath allows compat with Windows
            st.image(os.path.relpath(_img), os.path.basename(_img))

""")


def main() -> None:   # pragma: no cover
    """
    ```bash
    usage: onecode-start [-h] [--modules [MODULES [MODULES ...]]] [--dump] [--verbose]

    Start the OneCode Project in Streamlit mode.

    optional arguments:
      -h, --help            show this help message and exit
      --modules [MODULES [MODULES ...]]
                            Optional list of modules to import first
      --dump                Only generate the app.py file
      --verbose             Print verbose information when processing files
    ```

    """
    parser = argparse.ArgumentParser(description='Start the OneCode Project in Streamlit mode.')
    parser.add_argument(
        '--modules',
        nargs='*',
        default=[],
        help='Optional list of modules to import first'
    )
    parser.add_argument(
        '--dump',
        action="store_true",
        help='Only generate the app.py file'
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

    # args must be cleaned, otherwise conflict with streamlit.main_run()
    sys.argv = [sys.argv[0]]

    prepare_streamlit_file(os.getcwd(), 'app.py', args.verbose)

    if args.dump:
        print('Streamlit app file generated')
    else:
        Project().mode = Mode.EXECUTE
        os.environ['STREAMLIT_RUN_TARGET'] = 'app.py'
        os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '4000'
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = '0'

        main_run()
