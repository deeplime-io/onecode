from onecode import FileFilter, FileInput


def test_streamlit_file_input_single_selection_no_count():
    widget = FileInput(
        key="FileInput",
        value="/path/to/file.jpg",
        label="My FileInput",
        multiple=False,
        types=[FileFilter.IMAGE]
    )

    assert widget.streamlit("'fi'") == f"""
# FileInput fileinput
left, right = st.columns([3, 1])
with right:
    _button_fileinput = right.button('Select file', disabled=False, key="button_" + 'fi')

_file_fileinput = st.session_state["_file_" + 'fi'] if "_file_" + 'fi' in st.session_state else '''/path/to/file.jpg'''
if _button_fileinput:
    _file_fileinput = filedialog.askopenfilename(
        master=_root,
        filetypes=[{FileFilter.IMAGE}],
        title='Select file'
    )
    st.session_state["_file_" + 'fi'] = _file_fileinput

with left:
    fileinput = left.text_input('''My FileInput''', _file_fileinput, disabled=False, key='fi')
    if False and fileinput is not None: # is multiple?
        fileinput = ast.literal_eval(fileinput)
        if fileinput is not None:
            fileinput = list(fileinput)

"""  # noqa


def test_streamlit_file_input_multiple_selection_no_count():
    widget = FileInput(
        key="FileInput",
        value=["/path/to/file.jpg"],
        label="My FileInput",
        multiple=True,
        types=[FileFilter.IMAGE]
    )

    assert widget.streamlit("'fi'") == f"""
# FileInput fileinput
left, right = st.columns([3, 1])
with right:
    _button_fileinput = right.button('Select files', disabled=False, key="button_" + 'fi')

_file_fileinput = st.session_state["_file_" + 'fi'] if "_file_" + 'fi' in st.session_state else ('/path/to/file.jpg',)
if _button_fileinput:
    _file_fileinput = filedialog.askopenfilenames(
        master=_root,
        filetypes=[{FileFilter.IMAGE}],
        title='Select files'
    )
    st.session_state["_file_" + 'fi'] = _file_fileinput

with left:
    fileinput = left.text_input('''My FileInput''', _file_fileinput, disabled=False, key='fi')
    if True and fileinput is not None: # is multiple?
        fileinput = ast.literal_eval(fileinput)
        if fileinput is not None:
            fileinput = list(fileinput)

"""  # noqa


def test_streamlit_file_input_single_selection_with_count():
    widget = FileInput(
        key="FileInput",
        value="/path/to/file.jpg",
        label="My FileInput",
        multiple=False,
        types=[FileFilter.IMAGE],
        count=1
    )

    assert widget.streamlit("'fi'") == f"""
# FileInput fileinput
left, right = st.columns([3, 1])
with right:
    _button_fileinput = right.button('Select file', disabled=False, key="button_" + 'fi')

_file_fileinput = st.session_state["_file_" + 'fi'] if "_file_" + 'fi' in st.session_state else None
if _button_fileinput:
    _file_fileinput = filedialog.askopenfilename(
        master=_root,
        filetypes=[{FileFilter.IMAGE}],
        title='Select file'
    )
    st.session_state["_file_" + 'fi'] = _file_fileinput

with left:
    fileinput = left.text_input('''My FileInput''', _file_fileinput, disabled=False, key='fi')
    if False and fileinput is not None: # is multiple?
        fileinput = ast.literal_eval(fileinput)
        if fileinput is not None:
            fileinput = list(fileinput)

"""


def test_streamlit_file_input_multiple_selection_with_count():
    widget = FileInput(
        key="FileInput",
        value=["/path/to/file.jpg"],
        label="My FileInput",
        multiple=True,
        types=[FileFilter.IMAGE],
        count=1
    )

    assert widget.streamlit("'fi'") == f"""
# FileInput fileinput
left, right = st.columns([3, 1])
with right:
    _button_fileinput = right.button('Select files', disabled=False, key="button_" + 'fi')

_file_fileinput = st.session_state["_file_" + 'fi'] if "_file_" + 'fi' in st.session_state else None
if _button_fileinput:
    _file_fileinput = filedialog.askopenfilenames(
        master=_root,
        filetypes=[{FileFilter.IMAGE}],
        title='Select files'
    )
    st.session_state["_file_" + 'fi'] = _file_fileinput

with left:
    fileinput = left.text_input('''My FileInput''', _file_fileinput, disabled=False, key='fi')
    if True and fileinput is not None: # is multiple?
        fileinput = ast.literal_eval(fileinput)
        if fileinput is not None:
            fileinput = list(fileinput)

"""
