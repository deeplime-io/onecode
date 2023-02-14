# CLI

## Create a new project
::: onecode.cli.create.main
!!! example
    ```bash
    ? Enter the path where to create OneCode project /path/to/examples
    ? Enter your OneCode project name: HelloWorld
    ? Pick a name for your main flow: hello_world
    ⠋ Creating new OneCode project
    Initialized empty Git repository in /path/to/examples/HelloWorld/.git/

    ✅ Created HelloWorld OneCode project
    ```


## Add a flow to a project
::: onecode.cli.add.main
!!! example
    ```bash
    ? Enter the path of the existing OneCode project /path/to/examples/HelloWorld
    ? Enter the name of the new flow to add: second_step
    ? Choose before which flow:
      hello_world
    ❯ Put at the end
    ⠋ Adding new flow
    ✅ Added second_step flow
    ```


## Start a project with Streamlit
::: onecode.cli.start.main
!!! example
    ```bash
    # start project from the root folder
    onecode-start

    # in case of libraries extending OneCode
    onecode-start --module <library_name>
    ```


## Extract project parameters
::: onecode.cli.extract.main
!!! example
    ```bash
    # extract project parameters from the root folder
    onecode-extract params.json

    # in case of libraries extending OneCode
    onecode-extract params.json --module <library_name>
    ```


## How to reorganize flows?
This step can be done manually: open an issue if you feel like it is necessary to have it as a CLI command.
Open the `.onecode.json` file located at the root of the OneCode project in your favorite text editor.
You should see a fairly simple to understand JSON file:
```json
[
    {
        "file": "hello_world",
        "label": "hello_world",
        "attributes": {}
    },
    {
        "file": "second_step",
        "label": "second_step",
        "attributes": {}
    }
]
```

Manually re-order the flows, that's it!

!!! danger
    Do not change the `file` attribute of the flows, it will break the OneCode project. This name
    is synchronized with the Python filename in the `flows` folder.
