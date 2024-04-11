from onecode import HtmlOutput


def test_streamlit_html_output():
    widget = HtmlOutput(
        key="HtmlOutput",
        value="/path/to/file.html",
        label="My HtmlOutput"
    )

    assert widget.streamlit() == """
value = os.path.abspath(value)  # allows compat with Windows
if not os.path.exists(value) and not os.path.isfile(value):
    st.warning(f'Invalid file path: {{value}}')

else:
    st.markdown(
        f"<a href='file://{value}' target='_blank'>{os.path.basename(value)}</a>",
        unsafe_allow_html=True
    )
"""
