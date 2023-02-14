
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('postproc.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

import onecode


def run():
    x = onecode.slider('my l\'slid 10', 2, min=1, step=1, max=6)

    onecode.Logger.info(f'w = {x * 10}')

    onecode.Logger.info(
        onecode.file_input(
            'my input',
            'README.md',
            types=[('MD', '*.md'), onecode.FileFilter.IMAGE],
            multiple=False,
            optional='$my_l_slid_10$ * 2 < 3'
        )
    )

    onecode.Logger.info(
        onecode.file_input(
            'my input 2',
            [['x.py', 'y.py']],
            types=[onecode.FileFilter.PYTHON],
            multiple=True,
            count='2 * $my_l_slid_10$'
        )
    )
