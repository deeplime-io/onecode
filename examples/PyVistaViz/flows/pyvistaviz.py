
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('pyvistaviz.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

import onecode
import pyvista as pv
import numpy as np

from onecode import pyvista_vrml_output


def run():
    ## Create coordinate data
    x = np.arange(-10, 10, 0.25)
    y = np.arange(-10, 10, 0.25)
    x, y = np.meshgrid(x, y)
    z = np.sin(np.sqrt(x**2 + y**2))

    ## Set up plotter
    plotter = pv.Plotter(window_size=[400, 400])
    surface = pv.StructuredGrid(x, y, z)
    plotter.add_mesh(surface, color='teal', show_edges=True)

    plotter.export_vrml(pyvista_vrml_output('surface', "surface.vrml"))
