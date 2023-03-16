
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('las_convert.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

import os

from onecode import folder_input, csv_output, Logger
import lasio


def run():
    input_dir = folder_input('las', 'las/')
    las_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.las')]

    for f in las_files:
        Logger.info(f'processing {f}...')
        las = lasio.read(f)

        las.to_csv(csv_output('las', f'{os.path.basename(f)}.csv'))

    Logger.info('Done')
