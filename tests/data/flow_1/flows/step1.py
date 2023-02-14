
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('preproc.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

import time

import onecode as oc


def run():
    df = oc.csv_reader("csv", "input_test.csv")

    if df is not None:
        col_X = oc.dropdown('Column X', 'x', options='$csv$.columns', multiple=False)

        # line commented to test and ensure it is not interpreted by OneCode
        # multi = oc.dropdown('XYZ', 'ni', options='$csv$.columns', multiple=True)

        oc.Logger.info(f'selected column is: {col_X}')
        oc.Logger.info(f'Max of selected column is: {df[col_X].max()}')

    for x in range(7):
        time.sleep(0.5)
        oc.Logger.info(f'info: {x}')

    oc.Logger.info(oc.csv_output('My CSV', 'test.csv'))

    return 0
