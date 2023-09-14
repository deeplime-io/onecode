from onecode import PyvistaVrmlOutput


def test_streamlit_pyvista_vrml_output():
    widget = PyvistaVrmlOutput(
        key="PyvistaVrmlOutput",
        value="/path/to/file.json",
        label="My Pyvista VRML Output"
    )

    assert widget.streamlit() == """
_scene = pv.Plotter()
_scene.import_vrml(value)
_scene.reset_camera()
stpyvista(_scene, key='{key}')

"""
