# Organizing data

It is strongly advised to setup your input/output data files hierarchy relative to a root folder,
so that when you deploy your application, experts can simply specify a different root data path and
things will work out great. For instance:

```python
import os
from onecode import file_input, Project, Mode

project = Project()
project.mode = Mode.EXECUTE

file =  os.path.join('region', 'model.h5')
x = file_input('x', file)
```
will automatically append the path `region/model.h5` to your Project data path.
```python
print(f'Are path equals? {x == os.path.join(project.data_root, file)}')
```

```py title="Output"
Are path equals? True
```

From there, any experts can have a data folder with the same hierarchy anywhere on their disk and
launch the script by simply changing the data path at runtime:
```bash
ONECODE_PROJECT_DATA=/path/to/my/data python main.py
```
Without changing the code, the OneCode project can execute properly on different machines.

On the other hand, as soon as you specify an absolute path for your input files, the Project data
path is ignored. There could be some special cases for doing that, but most of the time you should
use relative paths.

!!! note
    Input elements such as `csv_reader` and `file_input` make the path relative to
    `Project().data_root`.

    Output elements such as `csv_output`, `file_output`, `image_output` and `text_output` make the
    path relative to `{Project().data_root}/{Project.current_flow}/outputs`.

!!! tip
    How is the Project data path determined? The data path is initialized according to the following
    rules ordered by priority:

    1. to `ONECODE_PROJECT_DATA` if provided in the Environment variables
    2. to the `data` folder located in the same directory from where the project is run if existing
    (typically the OneCode project data folder)
    3. to the current working directory for all other cases
