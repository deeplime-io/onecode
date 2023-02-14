###########################################
#    !! THIS FILE IS AUTO-GENERATED !!    #
###########################################

import ast
import json
import logging
import os
import tkinter as tk
import traceback
import uuid
from tkinter import filedialog
from typing import Dict, List

import numpy as np
import pydash
import streamlit as st
from main import main
from pyarrow import csv as pacsv
from streamlit_image_select import image_select
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select

from onecode import ColoredFormatter

_root = tk.Tk()
_root.withdraw()
_root.wm_attributes('-topmost', 1)

_DATA_ = {}
_placeholders = {}


def _write_logs(id: str) -> None:
    if f'__logs__{id}' in st.session_state:
        with _placeholders[id].container():
            st.markdown(
                f'''<div style="
                    background-color:black;
                    padding:1em;
                    margin-bottom:1em;
                    font-family:Source Code Pro, monospace;
                    font-size:0.8em">
                        {''.join(st.session_state[f'__logs__{id}'])}
                </div>''',
                unsafe_allow_html=True
            )


def _clear_logs(id: str) -> None:
    if f'__logs__{id}' in st.session_state:
        st.session_state[f'__logs__{id}'] = []
        _write_logs(id)


def _log(
    id: str,
    type: int,
    msg: str
) -> None:
    if id != st.session_state['__current_step_id__']:
        return

    if f'__logs__{id}' not in st.session_state:
        st.session_state[f'__logs__{id}'] = []

    color = "white"
    if type == logging.DEBUG:
        color="grey"
    elif type == logging.WARNING:
        color = "orange"
    elif type == logging.ERROR or type == logging.CRITICAL:
        color = "red"

    msg = msg.split("\n")
    st.session_state[f'__logs__{id}'].append(
        f'<span style="color:{color}">{"<br />".join(msg)}</span><br />'
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
        tree.append({
            "label": path_head,
            "value": file_id,
        })

    elif not path_head:  # means path starts with leading '/' => ignore
        _file_to_tree(file_id, path_split[1], cur_path, tree)

    else:
        node = pydash.find(tree, {"label": path_head})
        cur_path_agg = os.path.sep.join([cur_path, path_head])

        if node is None:
            n = {
                "label": path_head,
                "value": cur_path_agg,
                "children": []
            }
            tree.append(n)
            _file_to_tree(file_id, path_split[1], cur_path_agg, n["children"])

        else:
            _file_to_tree(file_id, path_split[1], cur_path_agg, node["children"])


def _show_img(path: str) -> None:
    _id = st.session_state.get('__current_step_id__')

    if not os.path.exists(path) and not os.path.isfile(path):
        st.warning(f'Invalid file path: {path}')

    elif _id is not None:
        _imgs = st.session_state.get(f'__selected_images__{_id}__', [])
        _imgs.append(path)
        st.session_state[f'__selected_images__{_id}__'] = pydash.uniq(_imgs)


with st.sidebar:
    _selected = option_menu("Main Menu", ["Step1", "Step2", "Step3"])

    # making a button despite this comment
    # https://github.com/streamlit/streamlit/issues/468#issuecomment-807166632
    if st.button('Stop Application'):
        os._exit(0)



def _CsvOutput(key=None, label=None, value=None, kind=None, tags=None):
    
    value = os.path.relpath(value)  # allows compat with Windows
    if not os.path.exists(value) and not os.path.isfile(value):
        st.warning(f'Invalid file path: {{value}}')
    
    else:
        df = pacsv.read_csv(value).to_pandas()
        file_size = df.size // 1e6
        if file_size > 200:
            st.write(f'File too big ({file_size} Mo), data has been truncated to the first 10k rows')
            df = df[:10000]
    
        st.subheader(f'{label} - {os.path.basename(value)}')
        st.dataframe(df)
    
    


if _selected == "Step1":
        
    # CsvReader csv
    _file_csv = st.file_uploader(
        f'''csv''' + ': select CSV file',
        type=['csv'],
        disabled=False,
        key='csv'
    )
    if _file_csv is not None:
        csv = pacsv.read_csv(_file_csv).to_pandas()
        if _file_csv.size // 1e6 > 200:
            st.write(
                f'File too big ({_file_csv.size // 1e6} Mo)'
                ', data has been truncated to the first 10k rows'
            )
            csv = csv[:10000]
        st.dataframe(csv)
    else:
        csv = None
    
    
    _DATA_['csv'] = csv if not (False) else None
    
    
    try:
        _options_column_x = _DATA_["csv"].columns
    except:
        _options_column_x = []
    
    if False: # is dropdown multiple?
        _default_column_x = [v for v in '''x''' if v in _options_column_x]
    else:
        _default_column_x = pydash.find_index(_options_column_x, lambda x: x == '''x''')
        _default_column_x = _default_column_x if _default_column_x >= 0 else 0
    
    # Dropdown column_x
    column_x = st.selectbox(
        '''Column X''',
        index=_default_column_x,
        options=_options_column_x,
        disabled=False,
        key='column_x'
    )
    
    
    _DATA_['column_x'] = column_x if not (False) else None
    
    
    _step_id = 'step1'
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
                _result =  main(_DATA_, _step_id, handler)
                st.info('Run finished')

                _nodes = []
                _json_output = []
                if os.path.exists(_result):
                    with open(_result) as f:
                        _json_output = pydash.sort_by(
                            json.loads(f"[{', '.join([line.rstrip() for line in f])}]"),
                            'value'
                        )

                    for _out in _json_output:
                        _filepath = _out.get('value')
                        if os.path.exists(_filepath):
                            _relpath = os.path.relpath(_filepath, os.getcwd())
                            _out['_id'] = str(uuid.uuid4())
                            _file_to_tree(_out['_id'], _relpath, '', _nodes)

                st.session_state[f'__nodes__{_step_id}__'] = _nodes
                st.session_state[f'__nodes_flat__{_step_id}__'] = _json_output

            except Exception as _e:
                st.error(
                    '\n'.join(
                        traceback.format_exception(
                            etype=type(_e),
                            value=_e,
                            tb=_e.__traceback__
                        )
                    )
                )

    _return_select = tree_select(
        st.session_state.get(f'__nodes__{_step_id}__', []),
        expand_on_click=True,
        only_leaf_checkboxes=True,
        show_expand_all=True
    )

    _shown_files = []
    for _sel in _return_select.get('checked'):
        _n = pydash.find(
            st.session_state.get(f'__nodes_flat__{_step_id}__', []),
            {"_id": _sel}
        )
        if _n is not None:
            _shown_files.append(_n['value'])

            _fname = f"_{_n['kind']}"
            if _fname in locals():
                locals()[_fname](**pydash.omit(_n, ['_id']))

    # keep only added images still selected in the tree
    _selected_imgs = st.session_state.get(f'__selected_images__{_step_id}__', [])
    _selected_imgs = pydash.intersection(_selected_imgs, _shown_files)
    st.session_state[f'__selected_images__{_step_id}__'] = _selected_imgs

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




if _selected == "Step2":
        
    # Slider my_slider_1
    my_slider_1 = st.slider(
        '''My slider"1''',
        min_value=0.0,
        max_value=6.0,
        value=0.5,
        step=0.1,
        disabled=False,
        key='my_slider_1'
    )
    
    
    _DATA_['my_slider_1'] = my_slider_1 if not (False) else None
    
    
    # Slider my_slider_2
    my_slider_2 = st.slider(
        '''My slider 2''',
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        disabled=_DATA_["my_slider_1"] * 2 < 3,
        key='my_slider_2'
    )
    
    
    _DATA_['my_slider_2'] = my_slider_2 if not (_DATA_["my_slider_1"] * 2 < 3) else None
    
    
    _step_id = 'step2'
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
                _result =  main(_DATA_, _step_id, handler)
                st.info('Run finished')

                _nodes = []
                _json_output = []
                if os.path.exists(_result):
                    with open(_result) as f:
                        _json_output = pydash.sort_by(
                            json.loads(f"[{', '.join([line.rstrip() for line in f])}]"),
                            'value'
                        )

                    for _out in _json_output:
                        _filepath = _out.get('value')
                        if os.path.exists(_filepath):
                            _relpath = os.path.relpath(_filepath, os.getcwd())
                            _out['_id'] = str(uuid.uuid4())
                            _file_to_tree(_out['_id'], _relpath, '', _nodes)

                st.session_state[f'__nodes__{_step_id}__'] = _nodes
                st.session_state[f'__nodes_flat__{_step_id}__'] = _json_output

            except Exception as _e:
                st.error(
                    '\n'.join(
                        traceback.format_exception(
                            etype=type(_e),
                            value=_e,
                            tb=_e.__traceback__
                        )
                    )
                )

    _return_select = tree_select(
        st.session_state.get(f'__nodes__{_step_id}__', []),
        expand_on_click=True,
        only_leaf_checkboxes=True,
        show_expand_all=True
    )

    _shown_files = []
    for _sel in _return_select.get('checked'):
        _n = pydash.find(
            st.session_state.get(f'__nodes_flat__{_step_id}__', []),
            {"_id": _sel}
        )
        if _n is not None:
            _shown_files.append(_n['value'])

            _fname = f"_{_n['kind']}"
            if _fname in locals():
                locals()[_fname](**pydash.omit(_n, ['_id']))

    # keep only added images still selected in the tree
    _selected_imgs = st.session_state.get(f'__selected_images__{_step_id}__', [])
    _selected_imgs = pydash.intersection(_selected_imgs, _shown_files)
    st.session_state[f'__selected_images__{_step_id}__'] = _selected_imgs

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




if _selected == "Step3":
        
    # Slider my_l_slid_10
    my_l_slid_10 = st.slider(
        '''my l\'slid 10''',
        min_value=1.0,
        max_value=6.0,
        value=2.0,
        step=1.0,
        disabled=False,
        key='my_l_slid_10'
    )
    
    
    _DATA_['my_l_slid_10'] = my_l_slid_10 if not (False) else None
    
    
    # FileInput my_input
    left, right = st.columns([3, 1])
    with right:
        _button_my_input = right.button('Select file', disabled=_DATA_["my_l_slid_10"] * 2 < 3, key="button_" + 'my_input')
    
    _file_my_input = st.session_state["_file_" + 'my_input'] if "_file_" + 'my_input' in st.session_state else '''../../data/flow_1/data/README.md'''
    if _button_my_input:
        _file_my_input = filedialog.askopenfilename(
            master=_root,
            filetypes=[('MD', '*.md'), ('Image', '.jpg .png .jpeg')],
            title='Select file'
        )
        st.session_state["_file_" + 'my_input'] = _file_my_input
    
    with left:
        my_input = left.text_input('''my input''', _file_my_input, disabled=_DATA_["my_l_slid_10"] * 2 < 3, key='my_input')
        if False and my_input is not None: # is multiple?
            my_input = ast.literal_eval(my_input)
            if my_input is not None:
                my_input = list(my_input)
    
    
    _DATA_['my_input'] = my_input if not (_DATA_["my_l_slid_10"] * 2 < 3) else None
    
    
    _DATA_['my_input_2'] = []
    for _c in range(int(2 * _DATA_["my_l_slid_10"])):
            
        # FileInput my_input_2
        left, right = st.columns([3, 1])
        with right:
            _button_my_input_2 = right.button('Select files', disabled=False, key="button_" + f'my_input_2_{_c}')
        
        _file_my_input_2 = st.session_state["_file_" + f'my_input_2_{_c}'] if "_file_" + f'my_input_2_{_c}' in st.session_state else None
        if _button_my_input_2:
            _file_my_input_2 = filedialog.askopenfilenames(
                master=_root,
                filetypes=[('Python', '.py')],
                title='Select files'
            )
            st.session_state["_file_" + f'my_input_2_{_c}'] = _file_my_input_2
        
        with left:
            my_input_2 = left.text_input('''my input 2''', _file_my_input_2, disabled=False, key=f'my_input_2_{_c}')
            if True and my_input_2 is not None: # is multiple?
                my_input_2 = ast.literal_eval(my_input_2)
                if my_input_2 is not None:
                    my_input_2 = list(my_input_2)
        
        
        _DATA_['my_input_2'].append(my_input_2 if not (False) else None)
    
    _step_id = 'step3'
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
                _result =  main(_DATA_, _step_id, handler)
                st.info('Run finished')

                _nodes = []
                _json_output = []
                if os.path.exists(_result):
                    with open(_result) as f:
                        _json_output = pydash.sort_by(
                            json.loads(f"[{', '.join([line.rstrip() for line in f])}]"),
                            'value'
                        )

                    for _out in _json_output:
                        _filepath = _out.get('value')
                        if os.path.exists(_filepath):
                            _relpath = os.path.relpath(_filepath, os.getcwd())
                            _out['_id'] = str(uuid.uuid4())
                            _file_to_tree(_out['_id'], _relpath, '', _nodes)

                st.session_state[f'__nodes__{_step_id}__'] = _nodes
                st.session_state[f'__nodes_flat__{_step_id}__'] = _json_output

            except Exception as _e:
                st.error(
                    '\n'.join(
                        traceback.format_exception(
                            etype=type(_e),
                            value=_e,
                            tb=_e.__traceback__
                        )
                    )
                )

    _return_select = tree_select(
        st.session_state.get(f'__nodes__{_step_id}__', []),
        expand_on_click=True,
        only_leaf_checkboxes=True,
        show_expand_all=True
    )

    _shown_files = []
    for _sel in _return_select.get('checked'):
        _n = pydash.find(
            st.session_state.get(f'__nodes_flat__{_step_id}__', []),
            {"_id": _sel}
        )
        if _n is not None:
            _shown_files.append(_n['value'])

            _fname = f"_{_n['kind']}"
            if _fname in locals():
                locals()[_fname](**pydash.omit(_n, ['_id']))

    # keep only added images still selected in the tree
    _selected_imgs = st.session_state.get(f'__selected_images__{_step_id}__', [])
    _selected_imgs = pydash.intersection(_selected_imgs, _shown_files)
    st.session_state[f'__selected_images__{_step_id}__'] = _selected_imgs

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

