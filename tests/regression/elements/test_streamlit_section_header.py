from onecode import SectionHeader


def test_streamlit_text_input():
    widget = SectionHeader(
        key="SectionHeader",
        value="it's a header here"
    )

    assert widget.streamlit("'sectionheader'") == """
# Header sectionheader
sectionheader = "it's a header here"
st.header("it's a header here")

"""
