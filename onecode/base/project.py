# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import ast
import json
import os
import sys
from typing import Any, Dict, Optional, Set, Union

import pydash
from flufl.lock import Lock

from .decorator import check_type
from .enums import ConfigOption, Env, Mode
from .singleton import Singleton


class Project(metaclass=Singleton):
    """
    Single Project object to centralize OneCode project data, such as the data path,
    parameter values, registered elements, flow currently running, current running
    mode, etc.

    See [`reset()`][onecode.Project.reset] for Project default's initialization.

    Attributes:
        registered_elements: List of elements registered for processing.
        mode: Control how elements are processed.
        current_flow: ID of the flow currently running.
        data_root: Path to the data folder.
        data: Dictionnary containing the data values from interpreted elements.
        config: Dictionnary containing the project configuration.

    """

    def __init__(self):
        self._registered_elements = set()
        self.reset()

    def reset(
        self,
        keep_registered_elements: bool = False
    ):
        """
        Reset the project to its default values:
        - the data path is initialized in priority to `ONECODE_PROJECT_DATA` if provided in the
        Environment variables, otherwise to the `data` folder located in the same directory from
        where the project is run if existing (typically the OneCode project data folder), otherwise
        to the current working directory.
        - mode is `Mode.CONSOLE`.
        - currently running flow and data are None.
        - registered elements default to the OneCode ones unless `keep_registered_elements` is True.

        Args:
            keep_registered_elements: keep previously registered elements.

        """
        # data folder located at the same level as the starting script,
        # e.g. in the same folder as the main.py file
        root_dir = os.path.abspath(sys.argv[0])
        if os.path.isdir(root_dir):     # pragma: no cover
            data_dir = os.path.join(root_dir, 'data')
        else:
            data_dir = os.path.join(os.path.dirname(root_dir), 'data')

        if Env.ONECODE_PROJECT_DATA in os.environ:
            self._set_data_root(os.environ[Env.ONECODE_PROJECT_DATA])

        elif os.path.isdir(data_dir):
            self._set_data_root(data_dir)

        else:
            self._set_data_root(os.getcwd())

        if not keep_registered_elements:
            this_module = sys.modules[__name__].__name__.split('.')[0]
            self._registered_elements = {
                ent for ent in self._registered_elements if ent.startswith(f'{this_module}.')
            }

        self._mode = Mode.CONSOLE
        self._flow = None
        self._data = None

        # get string config from env variables starting with ONECODE_CONFIG_
        # get flag config from env variables starting with ONECODE_FLAG_
        self._config = {
            ConfigOption.FLUSH_STDOUT: False,
            ConfigOption.LOGGER_COLOR: True,
            ConfigOption.LOGGER_TIMESTAMP: True,
            ConfigOption.CHECK_MODULES: True,
            **{k[len("ONECODE_CONFIG_"):]: os.environ[k]
                for k in os.environ if k.startswith("ONECODE_CONFIG_")},
            **{k[len("ONECODE_FLAG_"):]: bool(ast.literal_eval(os.environ[k]))
                for k in os.environ if k.startswith("ONECODE_FLAG_")},
        }

    @property
    def registered_elements(self) -> Set[str]:
        """
        Get the list of registered elements (`InputElement` and `OutputElement`).
        Once a library is registered, it is required to register the elements that need to be
        processed.

        By default, it returns all Input/Output Elements of `onecode` library.

        """
        return self._registered_elements

    @check_type
    def register_element(
        self,
        element_name: str
    ) -> None:
        """
        Register the given element as part of the elements to be processed. The element must be of
        the form '<module>.<class_name>', e.g. `onecode_ext.MyInput`

        Args:
            element_name: Python name of the element (i-e class name).

        Raises:
            ValueError: if element is not of the form '<module>.<class_name>' of if the class name
                is already snake case.

        """
        element_parts = element_name.split('.')
        if len(element_parts) != 2:
            raise ValueError(
                f'Invalid element name: {element_name} must be of form "<module>.<class_name>"'
            )

        if element_parts[1] == pydash.snake_case(element_parts[1]):
            raise ValueError(
                f'Invalid element name: {element_parts[1]} must not be snake case'
            )

        self._registered_elements.add(element_name)

    @property
    def mode(self) -> Union[Mode, str]:
        """
        Get the currently set mode for the OneCode Project. A string is returned in case of custom
        modes. See [Mode][onecode.Mode] for more information.

        """
        return self._mode

    @mode.setter
    def mode(
        self,
        mode: Union[Mode, str]
    ) -> None:
        """
        Set the current mode for the OneCode Project. You can use a custom string for custom modes.
        See [Mode][onecode.enums.Mode] for more information.

        """
        self._mode = mode

    @property
    def current_flow(self) -> Optional[str]:
        """
        Get the currently running flow. If no flow is running, None is returned. It is automatically
        set when OneCode project is run through the main entry point (i-e
        `python main.py` or `onecode-start`)

        """
        return self._flow

    @current_flow.setter
    def current_flow(
        self,
        flow: str
    ) -> None:
        """
        Set the currently running flow. This is automatically set when OneCode project is run
        through the main entry point (i-e `python main.py` or `onecode-start`)

        """
        self._flow = flow

    @property
    def data_root(self) -> str:
        """
        Get the path to the root of the data folder. See [`reset()`][onecode.Project.reset] to know
        how the data path is initialized.

        """
        return self._data_root

    @check_type
    def _set_data_root(
        self,
        data_path: str
    ) -> None:
        """
        Protected method to set the data root path. It is unsafe to use this method and change
        the data path while running the OneCode project.

        Args:
            data_path: Path to the data root.

        Raises:
            NotADirectoryError: if the data path does not exist or is not a directory.


        """
        if not os.path.isdir(data_path):
            raise NotADirectoryError(f"Invalid data path: {data_path}")

        self._data_root = data_path

    @check_type
    def get_input_path(
        self,
        filepath: str
    ) -> str:
        """
        Get the constructed input path for the given file path. If the file path is absolute or
        null, the path is left unchanged, otherwise the path is considered relative to the data
        root path.

        Args:
            filepath: filename of file path to construct the input path from.

        Returns:
            The constructed input path to the file.

        """
        return filepath if not filepath or os.path.isabs(filepath) \
            else os.path.join(self.data_root, filepath)

    @check_type
    def get_output_path(
        self,
        filepath: str
    ) -> str:
        """
        Get the constructed output path for the given file path. The path is always considered
        relative to the data output path (typically `<data_root>/outputs/`).

        Args:
            filepath: filename of file path to construct the output path from.

        Returns:
            The constructed output path to the file.

        """
        return None if filepath is None else os.path.join(self.data_root, 'outputs', filepath)

    def get_output_manifest(self) -> str:
        """
        Get the path to the current flow manifest file, typically
        `<data_root>/outputs/<flow>/MANIFEST.txt`. If the path does not exist, it is automatically
        created.

        The manifest file is a collection of output data attributes: there would typically be one
        entry per output file, each entry containing attributes information. Each line is a JSON
        entry but the entire file is not a JSON.

        !!! example
            ```json
            {"key": "x", "value": "file1.csv", "kind": "FileOutput", "tags": ["CSV"],
                "mimetype": "text/csv" }
            {"key": "y", "value": "file2.txt", "kind": "FileOutput", "tags": ["TXT"],
                "mimetype": "text/plain" }
            ...
            ```

        Returns:
            Path to the output MANIFEST.txt file for the currently running flow.

        """

        output_manifest = self.get_output_path(
            os.path.join(self.current_flow, "MANIFEST.txt")
        )

        # create output directory if not already present
        manifest_dir = os.path.dirname(output_manifest)
        if not os.path.isdir(manifest_dir):
            os.makedirs(os.path.join(manifest_dir, '.locks'), exist_ok=True)

        return output_manifest

    @property
    def data(self) -> Optional[Dict[str, Any]]:
        """
        Get the Project current data. Data is typically set either at the start when running in
        mode `LOAD_THEN_EXECUTE` or incrementaly after each call to any input element.

        Data is simply a key-value dictionnary.

        """
        return self._data

    @property
    def config(self) -> Optional[Dict[str, Any]]:
        """
        Get the Project current configuration options.

        Config is simply a key-value dictionnary.

        """
        return self._config

    @data.setter
    def data(
        self,
        data: Dict[str, Any]
    ) -> None:
        """
        Set the Project data. It is typically done at the start when running in
        mode `LOAD_THEN_EXECUTE`.

        """
        self._data = data

    @check_type
    def add_data(
        self,
        key: str,
        value: Any
    ) -> None:
        """
        Add a key-value pair to the data dictionnary.

        Args:
            key: Unique key to set the attach the value to.
            value: Value corresponding to the given key.

        Raises:
            ValueError: if the key is empty or None.

        """
        if not key:
            raise ValueError('Key cannot be null')

        if self._data is None:
            self._data = {}

        self._data[key] = value

    @check_type
    def set_config(
        self,
        key: Union[ConfigOption, str],
        value: Any
    ) -> None:
        """
        Add a key-value pair to the config dictionnary.

        Args:
            key: Unique key to set the attach the value to.
            value: Value corresponding to the given key.

        Raises:
            ValueError: if the key is empty or None.

        """
        if not key:
            raise ValueError('Key cannot be null')

        self._config[key] = value

    @check_type
    def get_config(
        self,
        key: Union[ConfigOption, str]
    ) -> Any:
        """
        Get the value corresponding to the key config.

        Args:
            key: Unique key to get the value from.

        Raises:
            ValueError: if the key does not exists.

        """
        if key not in self._config:
            raise KeyError(key)

        return self._config[key]

    @check_type
    def write_output(
        self,
        output: Dict
    ) -> None:
        """
        Write data to the output manifest file corresponding to the currently running flow.
        This function is thread and process-safe, i-e if there is concurrent writing to the
        manifest file (e.g. parallelization through multiprocessing), writing will be queued so
        that there is no overwrite or other side-effect. The file will therefore be valid and
        without data loss.

        Although typically this function is automatically called during the OutputElement
        execution, it is possible to manully call it too to output custom data.

        Args:
            output: Output data to write to the manifest file.

        """
        manifest_dir = os.path.dirname(self.get_output_manifest())

        # manage concurrent access in case of multiprocessing
        with Lock(os.path.join(manifest_dir, '.locks', 'MANIFEST.lock'), lifetime=3):
            with open(self.get_output_manifest(), "a") as f:
                f.write(f'{json.dumps(output)}\n')
