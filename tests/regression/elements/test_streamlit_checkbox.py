from onecode import Checkbox


def test_streamlit_checkbox():
    widget = Checkbox(
        key="Checkbox",
        value=True,
        label="My Checkbox"
    )

    assert widget.streamlit("'cb'") == """
# Checkbox checkbox
checkbox = st.checkbox(
    '''My Checkbox''',
    True,
    disabled=False,
    key='cb'
)

"""
