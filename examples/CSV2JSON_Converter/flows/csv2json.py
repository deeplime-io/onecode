
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('json_beautifier.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues
from pathlib import Path

from csv2json import convert

from onecode import FileFilter, Logger, file_input, text_output


def run():
    csv_in = file_input('csv_in', 'test.csv', label='Input CSV File', types=[FileFilter.CSV])
    json_out = text_output('json_out', f'{Path(csv_in).stem}.json', label='Output JSON File')

    Logger.info(f'Input CSV: {csv_in}')
    Logger.info(f'Output JSON: {json_out}')

    with open(csv_in) as r, open(json_out, 'w') as w:
        convert(r, w)
