from onecode import VideoOutput


def test_streamlit_video_output():
    widget = VideoOutput(
        key="VideoOutput",
        value="/path/to/file.mmp4",
        label="My VideoOutput"
    )

    assert widget.streamlit() == "st.video(value)"
