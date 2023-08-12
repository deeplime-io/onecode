# Extending OneCode


## OneCode principle overview
![`OneCode` overview](https://github.com/deeplime-io/onecode/raw/main/docs/assets/onecode_chart.png)


## Extend with new elements inside a OneCode Project
Each OneCode Project contains by default a folder `onecode_ext` inside its `flows` folder. The
mechanism is already in place so that you can simply add your new elements and they will be
automatically registered as OneCode elements. Input and output elements respectively go to
`flows/onecode_ext/input_elements/` and `flows/onecode_ext/output_elements`folders. You only need
to follow these 2 instructions:

1. The Python filename must be snake case and the corresponding element class name must be Pascal
    case. For instance, `my_new_element.py` => `class MyNewElement`.

2. Re-implement the `abstractmethod` defined in the `InputElement` or `OutputElement` base class
    according its documentation.

Here is a simple example:
```python
# flows/onecode_ext/input_elements/my_header_element.py
from onecode import InputElement


class MyHeaderElement(InputElement):
    def __init__(
        self,
        key: str,
        value: str
    ):
        super().__init__(key, value)

    @property
    def _value_type(self) -> type:
        return str

    def _validate(
        self,
        value: str
    ) -> None:
        pass

```

Then call it in your flow code:
```python
# flows/my_flow.py
from onecode_ext import my_header_element


def run():
    x = my_header_element('x', 'My Header!'))
    # ...
```

As easy as that. If you're interested on how it works under the hood, check out the
[section below][registering-input-elements].

!!! tip
    For a real use-case example, look at the
    [`DeepLearning` project](https://github.com/deeplime-io/onecode/tree/main/examples/DeepLearning)


## Extend as a library
For use-cases going beyond the scope of a single OneCode Project, you may consider writing your own
library. For example, you could have specific elements used across many projects and/or dedicated
mode to be compatible with your internal tools such as a cloud platform.

To add new elements, you will manually code what `onecode_ext` does automatically for you:

* Set a separate folder for your input and output elements, then add the following code to its `__init__` files:
```python
# input elements
from onecode import import_input

import_input(__file__, __name__)
```
```python
# output elements
from onecode import import_output

import_output(__file__, __name__)
```
Refer to [Registering input elements][registering-input-elements] and [Registering output elements][registering-output-elements]
for more information.

* For any new element:
    1. The Python filename must be snake case and the corresponding element class name must be Pascal
    case. For instance, `my_new_element.py` => `class MyNewElement`.

    2. Re-implement the `abstractmethod` defined in the `InputElement` or `OutputElement` base class
        according its documentation.

From there, to ensure your module is taken into account by CLI commands, add `--module yourcode` to them:
```bash
# Start in UI mode
onecode-start --module <library_name>

# JSON parameter extraction
onecode-extract params.json --module <library_name>
```


You may also:

* add new [`Mode`][onecode.Mode]: define a mixin class and inherit all elements with the mixin
* add new CLI: you may use the [CLI Utilities][cli] or even start from the OneCode
    CLI original code as it is open source with MIT License.

!!! example
    Here is an [example of library called `yourcode`](https://github.com/deeplime-io/onecode/tree/main/examples/yourcode)
    extending OneCode and demonstrating:

    * a new CLI extracting parameters as TOML
    * a radio button widget accepting runtime [Expressionstips_and_tricks#using-runtime-expressions-in-elements)


## Registering input elements
```python
def import_input(
    init_file: str,
    module_name: str
) -> None:
```
::: onecode.utils.import_input


## Registering output elements
```python
def import_output(
    init_file: str,
    module_name: str
) -> None:
```
::: onecode.utils.import_output
