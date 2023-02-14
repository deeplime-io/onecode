
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('estimation.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

from onecode import Logger, Project

from .utils import xx


def run():
    Logger.info(Project().data_root)
    Logger.info('Debug !!')
    Logger.info('Info !!')
    Logger.warning('Warning !!')
    Logger.error('Error !!')
    Logger.critical('Critical !!')

    xx()
