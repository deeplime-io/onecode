from onecode import ImageOutput


def test_streamlit_image_output():
    widget = ImageOutput(
        key="ImageOutput",
        value="/path/to/file.jpg",
        label="My ImageOutput"
    )

    assert widget.streamlit() == "_show_img(value)"
