import os
import shutil

import pytest

from onecode import Env
from onecode.cli.create import create
from tests.utils.flow_cli import _clean_flow, _generate_flow_name


@pytest.mark.emulations
def test_execute_single_count():
    flow_name, flow_folder, flow_id = _generate_flow_name()

    tmp = _clean_flow(flow_folder)
    create(tmp, flow_name, cli=False)

    flow_dir = os.path.join(tmp, flow_folder)

    with open(
        os.path.join(flow_dir, 'flows', 'onecode_ext', 'input_elements', 'my_input_element.py'),
        'w'
    ) as f:
        f.write("""
from typing import Any, Union

from onecode import InputElement


class MyInputElement(InputElement):
    def __init__(
        self,
        key: str,
        value: Union[float, int]
    ):
        super().__init__(key, value)

    @property
    def value(self) -> Union[float, int]:
        return 3 * self._value + 5.5

    @property
    def _value_type(self) -> type:
        return Union[float, int]

    def _validate(
        self,
        value: Any
    ) -> None:
        pass

""")

    with open(os.path.join(flow_dir, 'flows', f'{flow_id}.py'), 'w') as f:
        f.write("""
from onecode_ext import *

def run():
    x = my_input_element('My Element', 14.3)
    with open("stdout.txt", 'w') as f:
        f.write(str(x))
    """)

    os.system(f'cd "{flow_dir}" && {Env.ONECODE_DO_TYPECHECK}=1 python main.py')

    with open(os.path.join(flow_dir, 'stdout.txt')) as f:
        assert f.read() == f"{3 * 14.3 + 5.5 }"

    shutil.rmtree(flow_dir)
