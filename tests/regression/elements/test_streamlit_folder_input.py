from onecode import FileFilter, FolderInput


def test_streamlit_folder_input_single_selection_no_count():
    widget = FolderInput(
        key="FolderInput",
        value="/path/to/folder/",
        label="My FolderInput"
    )

    assert widget.streamlit("'fi'") == f"""
# FolderInput folderinput
left, right = st.columns([3, 1])
with right:
    _button_folderinput = right.button('Select folder', disabled=False, key="button_" + 'fi')

_file_folderinput = st.session_state["_file_" + 'fi'] if "_file_" + 'fi' in st.session_state else '''/path/to/folder/'''
if _button_folderinput:
    _file_folderinput = filedialog.askdirectory(
        master=_root,
        title='Select folder'
    )
    st.session_state["_file_" + 'fi'] = _file_folderinput

with left:
    folderinput = left.text_input('''My FolderInput''', _file_folderinput, disabled=False, key='fi')
"""  # noqa

def test_streamlit_folder_input_single_selection_with_count():
    widget = FolderInput(
        key="FolderInput",
        value="/path/to/folder/",
        label="My FolderInput",
        count=1
    )

    assert widget.streamlit("'fi'") == f"""
# FolderInput folderinput
left, right = st.columns([3, 1])
with right:
    _button_folderinput = right.button('Select folder', disabled=False, key="button_" + 'fi')

_file_folderinput = st.session_state["_file_" + 'fi'] if "_file_" + 'fi' in st.session_state else None
if _button_folderinput:
    _file_folderinput = filedialog.askdirectory(
        master=_root,
        title='Select folder'
    )
    st.session_state["_file_" + 'fi'] = _file_folderinput

with left:
    folderinput = left.text_input('''My FolderInput''', _file_folderinput, disabled=False, key='fi')
"""
