from onecode import TextInput


def test_streamlit_text_input():
    widget = TextInput(
        key="TextInput",
        value="it's a text here",
        label="My TextInput",
        max_chars=3000,
        placeholder="My Placeholder"
    )

    assert widget.streamlit("'textinput'") == """
# Text textinput
textinput = st.text_input(
    '''My TextInput''',
    "it's a text here",
    disabled=False,
    max_chars=3000,
    placeholder="My Placeholder",
    key='textinput'
)

"""


def test_streamlit_text_area():
    widget = TextInput(
        key="TextInput",
        value="it's a text here",
        label="My TextInput",
        max_chars=3000,
        placeholder="My Placeholder",
        multiline=400
    )

    assert widget.streamlit("'textinput'") == """
# Text textinput
textinput = st.text_area(
    '''My TextInput''',
    "it's a text here",
    disabled=False,
    max_chars=3000,
    placeholder="My Placeholder",
    height=400,
    key='textinput'
)

"""
