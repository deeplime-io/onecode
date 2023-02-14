## OneCode Extensions

Optionally put your input/output elements in this extension.

#### Usage
Simply import `onecode_ext`, e.g.

```python
# ./flows/my_flow.py

import onecode
from onecode_ext import my_input_element


def run():
    x = my_input_element('input_element', None, optional=True)

    # ...
```
