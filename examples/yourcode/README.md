# YourCode

Example of OneCode extension library demonstrating:

* a dynamic radio button element `DynamicRadioButton`: extends the regular `RadioButton` by
    allowing an Expression as options (`RadioButton` only accepts fixed options).
* a new CLI command to extract element parameters to TOML format.


## Installation

```bash
pip install onecode[tech-expert]
pip install /path/to/yourcode
```


## Usage in OneCode projects
```python
# Similar signature than RadioButton
# options now accept Expressions

dynamic_radio_button(
    key: str,
    value: Optional[Union[str, List[str]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    options: List[str] = [],
    horizontal: bool = False
)
```

## CLI

To ensure your module is taken into account, add `--module yourcode` to all CLI.
```bash
# Start with UI
onecode-start --module yourcode

# Regular JSON parameter extraction
onecode-extract params.json --module yourcode

# New TOML parameter extraction
yourcode-extract params.toml --module yourcode

```

## Run a project

```bash
# Run a project with default parameters (unchanged)
python main.py

# Run a project with another parameter set (unchanged)
python main.py params.json
```
