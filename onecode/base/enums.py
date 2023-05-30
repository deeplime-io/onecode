# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from enum import Enum


class Env(str, Enum):
    """
    Available environment variables for OneCode projects:

    - `ONECODE_PROJECT_DATA`: use this variable to overwrite default data location
    :octicons-arrow-both-24: `"ONECODE_PROJECT_DATA"`
    - `ONECODE_CONFIG_FILE`: name of the file containing OneCode project configurations
    :octicons-arrow-both-24: `".onecode.json"`
    - `ONECODE_DO_TYPECHECK`: set to 1 to force runtime type-checking with Pydantic
    :octicons-arrow-both-24: `"ONECODE_DO_TYPECHECK"`
    - `ONECODE_LOGGER_NAME`: base logger name to avoid logging conflict with other loggers
    :octicons-arrow-both-24: `|OneCode|`

    """
    ONECODE_PROJECT_DATA    = "ONECODE_PROJECT_DATA"    # noqa: E-221
    ONECODE_CONFIG_FILE     = ".onecode.json"           # noqa: E-221
    ONECODE_DO_TYPECHECK    = "ONECODE_DO_TYPECHECK"    # noqa: E-221
    ONECODE_LOGGER_NAME     = "|OneCode|"               # noqa: E-221


class ConfigOption(str, Enum):
    """
    Available options to control the configuration of the project.

    - `FLUSH_STDOUT`: to force flushing the logger :octicons-arrow-both-24: `"FLUSH_STDOUT": False`
    - `LOGGER_COLOR`: to color the logs by default when resetting the logger
        :octicons-arrow-both-24: `"LOGGER_COLOR": True`
    - `LOGGER_TIMESTAMP`: to timestamp the logs :octicons-arrow-both-24: `"LOGGER_TIMESTAMP": True`

    """
    FLUSH_STDOUT        = "FLUSH_STDOUT"            # noqa: E-221
    LOGGER_COLOR        = "LOGGER_COLOR"            # noqa: E-221
    LOGGER_TIMESTAMP    = "LOGGER_TIMESTAMP"        # noqa: E-221


class Mode(str, Enum):
    """
    Available modes to run OneCode projects:

    - `CONSOLE`: return the initial element class. Typically used in the interactive Python console.
        It is the default `Project()` mode. :octicons-arrow-both-24: `"_console"`
    - `EXECUTE`: run the project with the default provided values. Typically used for running the
        Python scripts from the command line: `python main.py` :octicons-arrow-both-24: `"_execute"`
    - `LOAD_THEN_EXECUTE`: read parameters previously loaded in `Project().data`. Typically used for
        running the Python scripts from the command line: `python main.py params.json`
        :octicons-arrow-both-24: `"_load_then_execute"`
    - `EXTRACT`: extract parameters and their default value to JSON. It may be used either through
        regular Python scripts or the CLI. :octicons-arrow-both-24: `"_extract"`
    - `EXTRACT_ALL`: extract parameters, their default value and all their attributes
        (kind, name, etc.) to JSON. It may be used either through regular Python scripts or the CLI.
        :octicons-arrow-both-24: `"_extract_all"`
    - `STREAMLIT`: generate the Streamlit app code and run it. Typically used through the
        `onecode-start` CLI. :octicons-arrow-both-24: `"_build_streamlit"`

    These modes correspond to the function names of the Input/Output Element objects (e.g.
    `InputElement._execute()`). Therefore you can easily extend Input/Output Element with new modes
    by simply implement new methods in a derived class and set the mode to it.

    !!! example
        ```py
        from onecode import InputElement, process_call_graph, Project


        class MyElement(InputElement):
            # ... inherit InputElement methods as needed

            def _my_new_mode(self):
                # implement the gist of your new mode here
                # ...


        def do_my_new_mode(onecode_project_path: str):
            Project().mode = '_my_new_mode'
            result = process_call_graph(onecode_project_path)

            # do something with result
            # ...
        ```

    """
    CONSOLE             = "_console"                 # noqa: E-221
    EXECUTE             = "_execute"                 # noqa: E-221
    LOAD_THEN_EXECUTE   = "_load_then_execute"       # noqa: E-221
    EXTRACT             = "_extract"                 # noqa: E-221
    EXTRACT_ALL         = "_extract_all"             # noqa: E-221
    STREAMLIT           = "_build_streamlit"         # noqa: E-221


class Keyword(str, Enum):
    """
    Reserved keywords for the Streamlit app.

    - `DATA`: Streamlit variable holding the data :octicons-arrow-both-24: `"_DATA_"`

    """
    DATA             = "_DATA_"                 # noqa: E-221


class ElementType(str, Enum):
    """
    Available element type variables. These element types are typically used by specific modes
    (e.g. `EXTRACT`, `EXTRACT_ALL` and `STREAMLIT` modes).

    - `INPUT`: `InputElement` type :octicons-arrow-both-24: `"INPUT"`
    - `OUTPUT`: `OutputElement` Type :octicons-arrow-both-24: `"OUTPUT"`

    """
    INPUT       = "INPUT"          # noqa: E-221
    OUTPUT      = "OUTPUT"         # noqa: E-221


class FileFilter(tuple):
    """
    Available file filters, typically used by FileInput Element in STREAMLIT mode. It allows to
    filter file selection within the Open File Dialog. File filters are a Tuple made of 2 parts:
    `(name of the filter, file extensions separated by whitespaces)`.

    * `CSV` :octicons-arrow-both-24: `("CSV", ".csv")`
    * `PYTHON`:octicons-arrow-both-24: `("Python", ".py")`
    * `IMAGE` :octicons-arrow-both-24: `("Image", ".jpg .png .jpeg")`
    * `ZIP` :octicons-arrow-both-24: `("ZIP", ".zip .gz .tar.gz .7z")`

    """
    CSV       = ("CSV", ".csv")                        # noqa: E-221
    PYTHON    = ("Python", ".py")                      # noqa: E-221
    IMAGE     = ("Image", ".jpg .png .jpeg")           # noqa: E-221
    ZIP       = ("ZIP", ".zip .gz .tar.gz .7z")        # noqa: E-221
