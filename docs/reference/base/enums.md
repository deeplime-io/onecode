# Enumerations

!!! info "How to use Enums"
    Enums can be used in functions as Python object (int, float or strings) or as OneCode attribute.

    For example
    ```python
    from oncode import file_input, FileFilter

    widget = file_input(
        key="FileInput",
        value="/path/to/file1.txt",
        types=[FileFilter.IMAGE]
    )

    ```

    is equivalent to
    ```python
    from oncode import file_input, FileFilter

    widget = file_input(
        key="FileInput",
        value="/path/to/file1.txt",
        types=[("Image", ".jpg .png .jpeg")]
    )

    ```

::: onecode.base.enums
