import importlib.util
import os
import shutil
import sys
import tempfile
import uuid

from slugify import slugify

from onecode import Project


def _clean_flow(flow: str):
    tmp = tempfile.gettempdir()
    path = os.path.join(tmp, flow)

    if os.path.exists(path):
        shutil.rmtree(path)

    return tmp


def _generate_flow_name():
    name = f"My Flow Id_{uuid.uuid4().hex[:6]}"
    flow_name = slugify(name, lowercase=False, separator=' ')
    flow_folder = slugify(name, lowercase=False, separator='_')
    flow_id = slugify(flow_folder, separator='_')

    return flow_name, flow_folder, flow_id


def _generate_csv_file(
    flow: str,
    to_file: str,
    empty: bool = False
) -> str:
    out_file = os.path.join(flow, 'data', to_file)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        f.write("A,B,C\n")

        if not empty:
            f.write("0,1,2\n")
            f.write("3,4,5\n")

    return out_file


def _drop_loaded_project_modules(main_module_name: str) -> None:
    for name in list(sys.modules):
        if (
            name == "flows"
            or name.startswith("flows.")
            or name == "onecode_ext"
            or name.startswith("onecode_ext.")
            or name == main_module_name
        ):
            del sys.modules[name]


def run_project(flow_dir: str, raw_args=None):
    """
    Run a generated OneCode project's ``main.py`` in this process.

    ``sys.argv[0]`` and the working directory match a ``python main.py`` launch so that
    ``Project`` resolves the data folder the same way.
    """
    flow_dir = os.path.abspath(flow_dir)
    main_path = os.path.join(flow_dir, "main.py")
    main_module_name = "_onecode_project_under_test"

    old_cwd = os.getcwd()
    old_argv0 = sys.argv[0]
    path_inserted = flow_dir not in sys.path

    os.chdir(flow_dir)
    sys.argv[0] = main_path
    if path_inserted:
        sys.path.insert(0, flow_dir)

    _drop_loaded_project_modules(main_module_name)
    Project().reset()

    try:
        spec = importlib.util.spec_from_file_location(main_module_name, main_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[main_module_name] = module
        spec.loader.exec_module(module)
        return module._main([] if raw_args is None else raw_args)
    finally:
        _drop_loaded_project_modules(main_module_name)
        if path_inserted and flow_dir in sys.path:
            sys.path.remove(flow_dir)
        sys.argv[0] = old_argv0
        os.chdir(old_cwd)
