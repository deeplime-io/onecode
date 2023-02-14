from onecode import RadioButton


def test_streamlit_radio_button():
    widget = RadioButton(
        key="RadioButton",
        value="B",
        label="My RadioButton",
        options=["A", "B", "C"]
    )

    assert widget.streamlit("'radiobutton'") == """
# RadioButton radiobutton
radiobutton = st.radio(
    '''My RadioButton''',
    options=['A', 'B', 'C'],
    index=1,
    disabled=False,
    horizontal=False,
    key='radiobutton'
)

"""
