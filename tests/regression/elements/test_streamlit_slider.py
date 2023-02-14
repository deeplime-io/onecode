from onecode import Slider


def test_streamlit_number_input():
    widget = Slider(
        key="Slider",
        value=0.6,
        label="My Slider",
        min=0.1,
        max=0.8,
        step=0.1
    )

    assert widget.streamlit("'slider'") == """
# Slider slider
slider = st.slider(
    '''My Slider''',
    min_value=0.1,
    max_value=0.8,
    value=0.6,
    step=0.1,
    disabled=False,
    key='slider'
)

"""
