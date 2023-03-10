# Output Elements

Available output elements for OneCode projects:

* [csv_output][csv_output]
* [file_output][file_output]
* [image_output][image_output]
* [text_output][text_output]


## csv_output
```python
def csv_output(
    key: str,
    value: str,
    label: Optional[str] = None,
    tags: Optional[List[str]] = None
)
```
::: onecode.elements.output.csv_output.CsvOutput.__init__


## file_output
```python
def file_output(
    key: str,
    value: str,
    label: Optional[str] = None,
    tags: Optional[List[str]] = None
)
```
::: onecode.elements.output.file_output.FileOutput.__init__


## image_output
```python
def image_output(
    key: str,
    value: str,
    label: Optional[str] = None,
    tags: Optional[List[str]] = None
)
```
::: onecode.elements.output.image_output.ImageOutput.__init__


## text_output
```python
def text_output(
    key: str,
    value: str,
    label: Optional[str] = None,
    tags: Optional[List[str]] = None,
    truncate_at: int = 50000
)
```
::: onecode.elements.output.text_output.TextOutput.__init__
