
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('myflow.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

from yourcode import dynamic_radio_button

from onecode import Logger, csv_reader


def run():
    csv_reader("csv", '/path/to/csv')
    your_choice = dynamic_radio_button('radiobutton', 'ColumnX', options='$csv$.columns')

    Logger.info(f'your choice is: {your_choice}')
