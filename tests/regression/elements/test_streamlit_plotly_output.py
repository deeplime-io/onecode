from onecode import PlotlyOutput


def test_streamlit_plotly_output():
    widget = PlotlyOutput(
        key="PlotlyOutput",
        value="/path/to/file.json",
        label="My PlotlyOutput"
    )

    assert widget.streamlit() == """
value = os.path.relpath(value)  # allows compat with Windows
if not os.path.exists(value) and not os.path.isfile(value):
    st.warning(f'Invalid file path: {{value}}')

else:
    fig = plotly.io.read_json(value)

    st.subheader(f'{label} - {os.path.basename(value)}')
    st.plotly_chart(fig)

"""
