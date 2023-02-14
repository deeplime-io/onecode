# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('hello_world.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

from slugify import slugify

from onecode import Logger, text_input, text_output


def run():
    name = text_input(
        key='name',
        value='',
        label='What is your name?',
        placeholder="Type in your name"
    )

    if not name:
        Logger.error('Please type in your name!')

    else:
        out_string = f'Hello {name}'
        Logger.info(out_string)

        with open(text_output('output', f'hello_{slugify(name, separator="_")}.txt'), 'w') as f:
            f.write(out_string)
