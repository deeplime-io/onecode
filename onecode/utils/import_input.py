# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
import sys
from glob import glob
from inspect import Signature, signature

import pydash

from ..base.decorator import check_type
from ..base.enums import ElementType
from ..base.project import Project


@check_type
def import_input(
    init_file: str,
    module_name: str
) -> None:
    """
    Use this function to register your `InputElement`. Here is what it does for you in details.

    For each file located in the same folder as the `init_file` path:

    1. import the corresponding class: the class name must be the Pascal-case of the filename
        (e.g. `file_input.py` => `class FileInput`)
    2. register the class as an element, i-e it will be recognized by the OneCode interpreter
    3. export the class as-is (allow for subclassing by a third-party)
    4. export a new function matching the filename: it wrapps around the class for convenience
        by simply initializing it, then calling it.

        !!! example
            ```py
            def file_input(*args, **kwargs):
                return FileInput(*args, **kwargs)()

            # This makes a convenient usage in the client code:
            x = onecode.file_input('test', 'file.txt')

            # Rather than writing:
            x = onecode.FileInput('test', 'file.txt')()
            ```

    5. export:
        1. a new variable specifying the type of element being `INPUT`.
        2. a new function returning the element import statements.
        3. a new function returning the element init statements.

        !!! example
            ```py
            file_input_type = ElementType.INPUT

            def _file_input_importdef():
                return FileInput.imports()
            file_input_imports = _file_input_importdef

            def _file_input_initdef():
                return FileInput.init()
            file_input_init = _file_input_initdef
            ```
        This is used internally by OneCode interpreter.

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
                def _x(*args, **kwargs):
                    return cls(*args, **kwargs)()

                # Allow introspection (Jupyter, inspect, etc. but not VSCode)
                _x.__annotations__ = cls.__init__.__annotations__
                _x.__doc__ = cls.__init__.__doc__
                _x.__signature__ = Signature([
                    p for name, p in signature(cls.__init__).parameters.items() if name != 'self'
                ])
                return _x

            def _typedef():
                return ElementType.INPUT

            setattr(sys.modules[module_name], _filename, _xdef(_cls))
            setattr(sys.modules[module_name], f'{_filename}_type', _typedef())
            setattr(sys.modules[module_name], _ent, _cls)

        except AttributeError:   # pragma: no cover
            pass
