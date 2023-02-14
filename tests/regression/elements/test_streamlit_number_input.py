from onecode import NumberInput


def test_streamlit_number_input():
    widget = NumberInput(
        key="NumberInput",
        value=0.6,
        label="My NumberInput",
        min=0.1,
        max=0.8,
        step=0.1
    )

    assert widget.streamlit("'numberinput'") == """
# NumberInput numberinput
numberinput = st.number_input(
    '''My NumberInput''',
    min_value=0.1,
    max_value=0.8,
    value=0.6,
    step=0.1,
    disabled=False,
    key='numberinput'
)

"""
