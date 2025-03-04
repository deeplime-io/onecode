# CLI


## Create a new project
::: onecode.cli.create.main
!!! example
    ```bash
    ? Enter the path where to create OneCode project: ~/
    ? Enter your OneCode project name: HelloWorld

    ⠋ Creating new OneCode project
    ✅ Created HelloWorld OneCode project

    ```


## Extract project parameters
::: onecode.cli.extract.main
!!! example
    ```bash
    # extract project parameters from the root folder
    onecode-extract params.json

    ```


## Archive project output data
::: onecode.cli.zip.main
!!! example
    ```bash
    # archive project output data
    onecode-zip

    ```

## Check project modules
::: onecode.cli.check.main
!!! example
    ```bash
    # modules required by project are in the Python environnement and/or requirements.txt
    onecode-check

    [INFO]  - |OneCode|.check.py:52 - ✅ argparse
    [INFO]  - |OneCode|.check.py:52 - ✅ importlib
    [INFO]  - |OneCode|.check.py:52 - ✅ json
    [INFO]  - |OneCode|.check.py:52 - ✅ onecode (1.1.0)
    [INFO]  - |OneCode|.check.py:52 - ✅ os
    ```

## Get project requirements
::: onecode.cli.require.main
!!! example
    ```bash
    # generate requirements.txt file
    onecode-require requirements.txt

    ```
