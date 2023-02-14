from onecode import TextOutput


def test_streamlit_text_output():
    widget = TextOutput(
        key="TextOutput",
        value="/path/to/file.txt",
        label="My TextOutput"
    )

    assert widget.streamlit() == """
value = os.path.relpath(value)  # allows compat with Windows
if not os.path.exists(value) and not os.path.isfile(value):
    st.warning(f'Invalid file path: {{value}}')

else:
    with open(value, 'r') as f:
        txt = f.read()

    if len(txt) > truncate_at:
        txt = txt[:truncate_at]
        st.warning(f'File trucated at {truncate_at} characters')

    st.subheader(f'{label} - {os.path.basename(value)}')
    st.code(txt)
"""
