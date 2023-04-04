# Input Elements

Available input elements for OneCode projects:

* [checkbox][checkbox]
* [csv_reader][csv_reader]
* [dropdown][dropdown]
* [file_input][file_input]
* [folder_input][folder_input]
* [number_input][number_input]
* [radio_button][radio_button]
* [slider][slider]
* [text_input][text_input]


## checkbox
```python
def checkbox(
    key: str,
    value: Optional[Union[bool, List[bool]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False
)
```
::: onecode.elements.input.checkbox.Checkbox.__init__


## csv_reader
```python
def csv_reader(
    key: str,
    value: Optional[Union[str, List[str]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    tags: Optional[List[str]] = None
)
```
::: onecode.elements.input.csv_reader.CsvReader.__init__


## dropdown
```python
def dropdown(
    key: str,
    value: Optional[Union[str, List[str], List[List[str]]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    options: Union[List, str] = [],
    multiple: bool = False
)
```
::: onecode.elements.input.dropdown.Dropdown.__init__


## file_input
```python
def file_input(
    key: str,
    value: Optional[Union[str, List[str], List[List[str]]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    types: List[Tuple[str, str]] = None,
    multiple: bool = False,
    tags: Optional[List[str]] = None
)
```
::: onecode.elements.input.file_input.FileInput.__init__


## folder_input
```python
def folder_input(
    key: str,
    value: Optional[Union[str, List[str]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False
)
```
::: onecode.elements.input.folder_input.FolderInput.__init__


## number_input
```python
def number_input(
    key: str,
    value: Optional[Union[float, List[float]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    min: float = None,
    max: float = None,
    step: float = None
)
```
::: onecode.elements.input.number_input.NumberInput.__init__


## radio_button
```python
def radio_button(
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
::: onecode.elements.input.radio_button.RadioButton.__init__


## slider
```python
def slider(
    key: str,
    value: Optional[Union[float, List[float]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    min: float = 0.,
    max: float = 1.,
    step: float = 0.1
)
```
::: onecode.elements.input.slider.Slider.__init__


## text_input
```python
def text_input(
    key: str,
    value: Optional[Union[str, List[str]]],
    label: Optional[str] = None,
    count: Optional[Union[int, str]] = None,
    optional: Union[bool, str] = False,
    hide_when_disabled: bool = False,
    max_chars: int = None,
    placeholder: str = None
)
```
::: onecode.elements.input.text_input.TextInput.__init__
