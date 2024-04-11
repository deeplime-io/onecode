--8<-- "README.md"

Well, well, which profile are you?

* [expert][onecode-for-experts]
* [tech-savvy/data scientist][onecode-for-tech-savviesdata-scientists]
* [developer][onecode-for-developers]


## OneCode Overview
![`OneCode` overview](https://github.com/deeplime-io/onecode/raw/main/docs/assets/onecode_chart.png)

---
## OneCode for Experts
### Installation
Hosted with :sparkling_heart: by [PyPI](https://pypi.org/project/onecode/), simply install with `pip`:
```bash
pip install onecode[tech-expert]
```


### Running a OneCode Project
You just received a OneCode Project and would like to run it? In a terminal, go to the root
of the OneCode Project (e.g. `cd /path/to/onecode/project`), then run it:

* interactively through the web interface: `onecode-start`
* in command line with the default parameter set: `python main.py`

!!! tip

    **Advanced usage**

    * Run with your own dataset:
        1. extract the default parameter set: `onecode-extract parameters.json`
        2. update the `parameters.json` file with your values, preferentially relative to a root data folder
        (see [Best Practices With Data][best-practices-with-data]).
        3. run with it:
            - either `python main.py parameters.json` if your data is located in the `./data` folder.
            - or `ONECODE_PROJECT_DATA=/path/to/data python main.py parameters.json` if your data
            is located under another folder.
    * Run a specific flow instead of the whole project: `python main.py --flow <flow_id>`
    * Get the full instructions set: `python main.py --help`
    * Set a OneCode configuration option or flag at runtime by prepending `ONECODE_CONFIG_` or `ONECODE_FLAG_`: `ONECODE_FLAG_LOGGER_COLOR=1 python main.py` will set automatically `Project().set_config(ConfigOption.LOGGER_COLOR, True)`


---
## OneCode for Tech-Savvies/Data Scientists
### Installation
Hosted with :sparkling_heart: by [PyPI](https://pypi.org/project/onecode/), simply install with `pip`:
```bash
pip install onecode[tech-expert]
```


### Creating a new OneCode Project
Installing a new OneCode skeleton to start from
```bash
onecode-create

# then follow the prompts
? Enter the path where to create OneCode project /path/to/examples
? Enter your OneCode project name: HelloWorld
? Pick a name for your main flow: hello_world
⠋ Creating new OneCode project
Initialized empty Git repository in /path/to/examples/HelloWorld/.git/

✅ Created HelloWorld OneCode project
```

To ensure everything is ok, run your project:
```bash
cd /path/to/examples/HelloWorld
python main.py

# You should see the following printed
[INFO] hello_world - hello_world.py:15 -
        #####################################################################
        ###> Hello from hello_world!
        ###> Fill in this run() function with something awesome!
        #####################################################################
```

Read onto the [next section][adding-code-to-your-project] to now add some code.

!!! tip

    **Advanced usage**

    * [Add a new flow][add-a-flow-to-a-project] to an existing OneCode project
    * [Re-organize your project flows][how-to-reorganize-flows]


### Adding code to your project
The created Project is a skeleton with a built-in mechanism to run it within the different possible
environments. It is therefore preferable **not to tamper** with the files at the root of the Project,
such as `main.py`, `app.py`, `.onecode.json`. Instead, consider your working area as being under the
`flows` folder: feel free to put your own script architecture in there and call your Python code from
the `run()` function.

!!! danger

    Be aware these 3 important points though:

    1. Do not change the flow filenames
    2. Do not change the function name `run()` in the flow Python file
    3. Do not change the folder name `onecode_ext` located in the `flows` folder nor the the existing
    files in it.

    **Long explanation**

    - a flow is recognized by the project through its filename (matching the flow ID)
    and the entry point is the `run()` defined function. So, you can put anything in your flow file,
    just make sure you keep the default defined function `run()` and the flow filename untouched.
    - `onecode_ext` is dedicated to extend/customize OneCode elements, so you can add new files under
    the `onecode_ext` folder, however don't edit the existing content and filenames.
    See the [Developers section][extending-onecode] if you feel adventurous.


So, what type of code should you be adding? Basically almost anything you want, the questions to ask
yourself are:

- what input files and parameters should be controllable by the experts?
- what output files should be made available to the experts?

Any of theses files or parameters can be exposed using the [OneCode Elements][input-elements].
Here is a quickstart from scratch, asking for a name and output `Hello <name>` in the console and a file:
```python
# HelloWorld/flows/hello_world.py

from onecode import Logger, text_input, text_output
from slugify import slugify


def run():
    name = text_input(
        key='name',
        value='',
        label='What is your name?',
        placeholder="Type in your name"
    )

    if not name:
        Logger.error('Please type in your name!')

    else:
        out_string = f'Hello {name}'
        Logger.info(out_string)

        with open(text_output('output', f'hello_{slugify(name, separator="_")}.txt'), 'w') as f:
            f.write(out_string)
```

Great, how do you test that now? According to the [Running a OneCode project section][running-a-onecode-project],
you have several options:

1. Run it interactively: `onecode-start`

![`HelloWorld` example in action](https://github.com/deeplime-io/onecode/raw/main/docs/assets/hello_world.gif)

2. Run it from the command line: `python main.py`. Wait a minute, you get:
```bash
[ERROR] hello_world - hello_world.py:14 - Please type in your name!
```
Of course, the default value is an empty string `''`:
```python
name = text_input(
    key='name',
    value='',
    label='What is your name?',
    placeholder="Type in your name"
)
```
How can you input your own parameter from the command line? You only need a JSON file made of the
key-values required by this process. You could create it manually which is ok for this example, however
for more complex projects, it could become tedious. Well, there is a magic command for that:
`onecode-extract params.json` will make this JSON for you populated with the default values:
```json
{
	"name": ""
}
```
Use your favorite text editor to write the values. This command is quite useful, especially when you
have multiple parameter sets, simply keep them in a JSON file and run them as needed.

From there, run the project with a given parameters set:
```bash
echo '{"name": "OneCode"}' > params.json
python main.py params.json
```

You should get:
```bash
[INFO] hello_world - hello_world.py:17 - Hello OneCode
```

Congratulations! With the same piece of code, you were able to run it in 3 different ways without
having to change the code! That's the spirit of OneCode. Check out the other examples to keep going.

!!! example

    More examples can be found [here](https://github.com/deeplime-io/onecode/tree/main/examples):

    * [`HelloWorld`](https://github.com/deeplime-io/onecode/tree/main/examples/HelloWorld): most basic
        example demonstrating an input text field and a process returning `"Hello <name>"` in the console
        logger as well as in a file of the same name `hello_<name>.txt`.
    * [`CSV to JSON Converter`](https://github.com/deeplime-io/onecode/tree/main/examples/CSV2JSON_Converter):
        example demonstrating simple input/output file fields and converting a CSV file to JSON.
    * [`Experimental Variography`](https://github.com/deeplime-io/onecode/tree/main/examples/ExperimentalVariography):
        example demonstrating a diversity of fields through a real geological use case.
    * [`DeepLearning`](https://github.com/deeplime-io/onecode/tree/main/examples/DeepLearning): example
        demonstrating some advanced capabilities such as:

            - multiple steps/flows: (1) train a neural net (2) predict.
            - conditional input: a number field dynamically controls the number of neural network layer
            parameters to input through the `count` parameter.
            - creating a custom `InputElement` as part of the `onecode_ext` modules.

---
## OneCode for Developers
### Installation
Hosted with :sparkling_heart: by [PyPI](https://pypi.org/project/onecode/), simply install with `pip`:
```bash
pip install onecode[developer]

# optionally if you would like to build the documentation locally
pip install onecode[docs]
```

Checkout the [tech-savvy part][creating-a-new-onecode-project] to get started coding OneCode
projects.


### Extending OneCode
There are 2 ways to extend OneCode:

- within a Project, using the `onecode_ext` mechanism. It allows to contain the customization
specific to a Project. For instance the [`DeepLearning` example](https://github.com/deeplime-io/onecode/tree/main/examples/DeepLearning),
has an element specific to Neural Network definition by combining sliders and dropdown menus to allow
experts to easily choose the Neural Network Dense Layers parameters.
- as a library:
    - add new input/output elements that would be useful for many projects.
    - add new modes to interpret elements in a different ways, e.g. output your custom input parameters
    format that your cloud platform can ingest, generate code for Panel or Dash, etc.

In any case, see [Extending OneCode][extending-onecode] for details on how to do that.


### Run OneCode self-tests
There are several types of tests:

* unit-tests: check the result validity of elementary operations.
* regressions: ensure the result of a function does not change through time, regardless of the
validity of the result.
* emulations: check result validity by emulating command line execution (e.g. `python main.py`).
These tests are made for Linux only.

```
# note: for all these commands, you may add '-n auto' to parallelize tests execution.

# run unit and regressions tests
python -m pytest tests

# run unit and regressions tests in parallel with Pydantic runtime type-checking
ONECODE_DO_TYPECHECK=1 python -m pytest tests -n auto

# run unit, regressions and emulation tests (Linux only)
python -m pytest tests --with-emulations

# run tests with coverage: this one is not compatible with the optional '-n auto'
coverage run -m pytest tests

# display the coverage report: note that it will not reach 100% because of some occasional
# platform-specific block code. Our CI runs the coverage on both Linux and Windows platforms,
# the reported coverage by our badge on top this page comes from these merged reports.
coverage report -m --omit="tests/*,*/**/__init__.py"
```


### Contributing to OneCode
OneCode is still in its early stages, so it is not opened to external contributions yet.
We would prefer to get feedback through [GitHub issues](https://github.com/deeplime-io/onecode/issues)
and see how OneCode is used and adopted first.
CI guidelines, coding standards and best practices will be provided once the repository is opened to
contributions.


---
## FAQ
> Why did you take Streamlit out of OneCode?

As Streamlit evolves rapidly, it is difficult to maintain and always run behind API changes.
Especially for community packages that we relied on and are barely or no longer maintained.
Streamlit is a great tool, period. However for our use case, it started to become difficult to
make OneCode evolve and keep Streamlit along, especially as our cloud platform has its own way
of working. You can actually still use Streamlit in Onecode: checkout the `onecode-streamlit`
project.

> Why do I need OneCode at all, I could just build my application with Streamlit?

That's absolutely true, Streamlit or other alternatives are perfectly suitable for that.
However beware of the limitations you can hit (file size handling, data caching, server overload, etc.).
There are scenarios that can work out without OneCode and that's definitely ok: pick the right tool for your use case.
When it comes to deploying your application for different purposes (batch, interactive, long process, large file processing, etc.)
or in different environments, you may find handy to not have to adapt your original code: it will
definitely save you time and frustration and let you focus on the gist of the work rather than the
deployment work.

> You talked about extending OneCode, what does it mean? How do I do that?

If you would like to add new elements or customize some elements' behavior, check out the
[developer section][onecode-for-developers]

> Are there any collaborative platform that run OneCode projects?

There is one in the works called at [onecode.rocks](https://onecode.rocks), centralizing data and OneCode projects.
Sign up there if you would like be part of the beta-testers cohort.


---
## Credits
Credits to all open-source libraries that helped build this project. Special thanks to:

- PyCG and its contributors for making the Call Graph algos essential to the OneCode mechanism.
- Geode Solutions and Spotlight Earth for testing the library and providing invaluable feedback.
