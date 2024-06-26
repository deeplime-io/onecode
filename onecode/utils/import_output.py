# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
import sys
from glob import glob

import pydash

from ..base.decorator import check_type
from ..base.enums import ElementType
from ..base.project import Project


@check_type
def import_output(
    init_file: str,
    module_name: str
) -> None:
    """
    Use this function to register your `OutputElement`. Here is what it does for you in details.

    For each file located in the same folder as the `init_file` path:

    1. import the corresponding class: the class name must be the Pascal-case of the filename
        (e.g. `file_output.py` => `class FileOutput`)
    2. register the class as an element, i-e it will be recognized by the OneCode interpreter
    3. export the class as-is (allow for subclassing by a third-party)
    4. export a new function matching the filename: it wrapps around the class for convenience
        by simply initializing it, then calling it. There is one important difference
        with `InputElement`: a mechanism is in place to allow calling the
        [`OutputElement.static_call()`][onecode.OutputElement.static_call] method when no
        argument are provided to the function. It is typically used internally by the OneCode
        interpreter to properly handle cases of dynamically defined parameters.

        !!! example
            ```py
            def file_output(*args, **kwargs):
                empty_ctor = not args and not kwargs
                return FileOutput.static_call(FileOutput) if empty_ctor \
                    else FileOutput(*args, **kwargs)()

            # This makes a convenient usage in the client code:
            x = onecode.file_output('test', 'file.txt')

            # Or for dynamically defined parameters:
            x = onecode.file_output('test', os.path.join(os.getcwd(), f'file_{my_var},txt')

            # Rather than writing:
            x = onecode.FileOutput('test', 'file.txt')()
            ```

    5. export:
        1. a new variable specifying the type of element being `OUTPUT`.
        2. a new function returning the element import statements.
        3. a new function returning the element init statements.

        !!! example
            ```py
            file_output_type = ElementType.OUTPUT

            def _file_output_importdef():
                return FileInput.imports()
            file_output_imports = _file_output_importdef

            def _file_output_initdef():
                return FileInput.init()
            file_output_init = _file_output_initdef
            ```
        This is used internally by OneCode interpreter

    Args:
        init_file: path to the __init__.py file located in the same directory as the input elements.
        module_name: Python name of the module to import the elements under. The module will then be
            available for importing using regular Python import statements.

   """
    this_module = sys.modules[module_name].__name__.split('.')[0]
    for _filename in [
        os.path.basename(f)[:-3] for f in glob(os.path.join(os.path.dirname(init_file), "*.py"))
        if os.path.isfile(f) and not f.endswith("__init__.py") and f.endswith(".py")
    ]:
        _ent = pydash.pascal_case(_filename)
        Project().register_element(f'{this_module}.{_ent}')

        _module = __import__('.'.join([module_name, _filename]), fromlist=[_filename])
        _cls = getattr(_module, _ent)

        try:
            def _xdef(cls):
                def _x(*args, **kwargs):    # pragma: no cover
                    empty_ctor = not args and not kwargs
                    return getattr(cls, "static_call")(cls) if empty_ctor \
                        else cls(*args, **kwargs)()
                return _x

            def _typedef():
                return ElementType.OUTPUT

            setattr(sys.modules[module_name], _filename, _xdef(_cls))
            setattr(sys.modules[module_name], f'{_filename}_type', _typedef())
            setattr(sys.modules[module_name], _ent, _cls)

        except AttributeError:   # pragma: no cover
            pass
