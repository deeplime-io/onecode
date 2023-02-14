from onecode import FileOutput


def test_streamlit_text_output():
    widget = FileOutput(
        key="FileOutput",
        value="/path/to/file.txt",
        label="My FileOutput"
    )

    assert widget.streamlit() == """
value = os.path.relpath(value)  # allows compat with Windows
if not os.path.exists(value) and not os.path.isfile(value):
    st.warning(f'Invalid file path: {{value}}')

else:
    st.subheader(f'{label} - {os.path.basename(value)}')
    st.info(f'''
File Info\n
- Path: {value}\n
- Size: {round(os.path.getsize(value) / 1e6, 4)} Mo
    ''')
"""
