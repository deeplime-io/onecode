![onecode_logo](https://github.com/deeplime-io/onecode/raw/1.x/docs/assets/onecode.jpg)

![GitHub release](https://img.shields.io/github/v/release/deeplime-io/onecode?sort=semver)
![PyPI - License](https://img.shields.io/pypi/l/onecode)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/onecode)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/deeplime-io/onecode/validation.yml?event=push&label=test%20status)
![Windows supported](https://img.shields.io/badge/platform-linux-%23f2c300?logo=linux)
![Linux supported](https://img.shields.io/badge/platform-windows-4287f5?logo=windows)
![MacOS supported](https://img.shields.io/badge/platform-macos-dedcde?logo=apple)
[![Maintainability](https://api.codeclimate.com/v1/badges/df236aa4b4ab765ba7db/maintainability)](https://codeclimate.com/github/deeplime-io/onecode/maintainability)
[![Coverage](https://codecov.io/gh/deeplime-io/onecode/branch/1.x/graph/badge.svg?token=BF54VNGWM5)](https://codecov.io/gh/deeplime-io/onecode)

---

OneCode, your gateway to Python application deployment on the Cloud!
Pssst, if you're not into rolling out your App but simply using them, check out the [OneCode Cloud user doc](https://deeplime-io.github.io/onecode/1.0.0/user_doc).

* [OneCode in One Minute](#onecode-in-one-minute)
* [Deploy on OneCode Cloud](#deploy-on-onecode-cloud)
* [Getting Started with the OneCode API](#getting-started-with-the-onecode-api)
* [Upgrading from 0.x](#upgrading-from-0x)
* [Work in Progress](#work-in-progress)
* [Getting Help](#getting-help)


## :snake: OneCode in One Minute

### Install OneCode

```bash
pip install onecode
```

### Create your first OneCode project

```bash
onecode-create

# then follow the prompts
? Enter the path where to create OneCode project: ~/
? Enter your OneCode project name: HelloWorld

⠋ Creating new OneCode project
✅ Created HelloWorld OneCode project
```

### Add your first OneCode Element

Edit the file `HelloWorld/flows/helloworld.py` such as
```python
from onecode import Logger, text_input


def run():
    Logger.info(f"Hello {text_input('your name', 'OneCoder')}!")

```

### Running your OneCode project

```bash
cd HelloWorld
python main.py

# You should see the following printed
[INFO] helloworld - |OneCode|.helloworld.py:5 - Hello OneCoder!
```

By default, the OneCode text input is `OneCoder` but now can take any other values without having to change the code.

:tada: Congratulations, you now are a OneCoder! :tada:


## :volcano: Deploy on OneCode Cloud

The following steps will show you how to get setup for the 1st time:

1. Ensure you install at least `onecode >= 1.0.0` and have a [GitHub](https://github.com) account
    * If you have an app with a previous `onecode` version, [upgrade from 0.x](#upgrading-from-0x).
    * [Create](#onecode-in-one-minute) your OneCode App (or use an existing one) and [push it to your GitHub account](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).

2. Request a beta-tester access [here](https://tally.so/r/mVJbWN).

3. Once you received your confirmation email, login on [onecode.rocks](https://www.onecode.rocks/login).

4. Register your first app
    * From the dashboard, navigate to **Apps** in the top menubar.

    ![OneCode Dashboard](https://github.com/deeplime-io/onecode/raw/1.x/docs/assets/dashboard.png)

    * Click on **Register New App**.

    ![OneCode Register App Step 1](https://github.com/deeplime-io/onecode/raw/1.x/docs/assets/app_rego_step_1.png)

    * On your first visit, you'll need to **Link GitHub Account** to your OneCode account.

    ![OneCode Register App Step 2](https://github.com/deeplime-io/onecode/raw/1.x/docs/assets/app_rego_step_2.png)

    * As you are redirected to GitHub, login to your GitHub account.

    ![OneCode Register App Step 3](https://github.com/deeplime-io/onecode/raw/1.x/docs/assets/app_rego_step_3.png)

    * **Authorize OneCode**.

    ![OneCode Register App Step 4](https://github.com/deeplime-io/onecode/raw/1.x/docs/assets/app_rego_step_4.png)

    * Upon authorization, you will be redirected back to OneCode with your GitHub identity.
    You now need to decide which repositories OneCode may access in order to build your app by
    clicking on **GitHub App**.
    ![OneCode Register App Step 5](https://github.com/deeplime-io/onecode/raw/1.x/docs/assets/app_rego_step_5.png)

    * Choose which repositories should be accessible by OneCode.
    Note that you can change these permissions at anytime.

    ![OneCode Register App Step 6](https://github.com/deeplime-io/onecode/raw/1.x/docs/assets/app_rego_step_6.png)

    * Select the repository and the branch corresponding to the OneCode App you want to deploy.
    Choose if needed a different image and Python version than the default one.

    ![OneCode Register App Step 7](https://github.com/deeplime-io/onecode/raw/1.x/docs/assets/app_rego_step_7.png)


5. The App will then appear in your personal Apps Workspace and be automatically built.
Each new commit that you push to the registered branch will automatically trigger a new build

:tada: :tada: :tada: Congratulations, you now are an Cloud OneCoder! :tada: :tada: :tada:


## :rocket: Getting Started with the OneCode API

OneCode relies on the following principles:

* **no-disruption**: OneCode doesn't force you to change the way you code. No matter what your code structure and
Python files hierarchy, OneCode can seamlessly be integrated with it.

* **controllable input parameters**: simply replace your hard-coded parameters with OneCode functions
(called **Elements**) so that their value can change without having to change the code. One Code, many ways to run!

* **automated interface**: OneCode push on the cloud, the interface will automatically be generated from the OneCode
Elements

* **easy deployment**: no need to change the code between your local machine and the cloud. Simply push your code
as-is on your synchronized GitHub account and your App (environment and UI!) will build automatically!


The most important part of the API are Input and Output Elements. They can be inlined within your code
or not, that's up to you (no-disruption!), see examples below:

* use [Input Elements](https://deeplime-io.github.io/onecode/1.0.0/reference/elements/element_list/#input-elements) whenever you need to expose a parameter
with a specific widget. For example:
```python
# instead of: df = pd.read_csv('test.csv')
df = csv_reader('your df', 'test.csv')

# instead of: for i in range(5):
for i in range(slider('N', 5, min=0, max=10)):  # inlined
    # do stuff

# instead of: choice = 'cat'
choice = dropdown('your choice', 'cat', options=['dog', 'cat', 'fish']) # not inlined
Logger.info(f'Your choice is {choice}')
```

* use [Output Elements](https://deeplime-io.github.io/onecode/1.0.0/reference/elements/element_list/#output-elements) whenever an output should be returned. For example:
```python
# instead of: plt.savefig('stuff.png')
plt.savefig(file_output('stuff', 'stuff.png'))  # inlined

# instead of: filepath = 'test.txt'
filepath = file_output('test', 'test.txt')  # not inlined
with open(filepath, 'w') as f:
    # do stuff
```

Check out the full API documentation [here](https://deeplime-io.github.io/onecode/1.0.0/reference/elements/input_elements_api)!


## :arrow_up: Upgrading from 0.x

* Ensure there is `requirements.txt` file at the root of your App and that it contains at least `onecode>=1,<2`.

* Change all Output Elements (e.g. `image_output()`, `text_output()`, etc.) to simply `file_output()`.

* Remove any `section_header()` element.

* Check out the [work in progress section](#work-in-progress) in case you were using advanced features.


## :construction: Work in Progress

As `onecode` is still transitioning to OneCode Cloud, early versions of the OneCode Cloud don't yet
support completely the following features:

* **Multi-steps**: adding more than one flow to your App will eventually be supported. In the meantime,
either split your app (one app per step) or merge all steps under a single one
(you may directly update the `.onecode.json` file or create a new app and move the code to it).

* **Folder Inputs**: as the cloud doesn't really have directory structures, it needs some special work.
In the meantime, replace with multiple selection `file_input` instead.

* **Custom Elements** (in custom plugin or `onecode_ext`): extra security precautions must be taken
to allow custom UI on the Cloud. It has therefore been disabled for now.  Replace them with regular elements until the Cloud is ready for them.

* **Dynamic `options`**: dynamic expressions in `options` of the `dropdown` element) is not fully
supported yet. You can still use it, in that case, the elements will ask user to fill out values
as regular text input (e.g. CSV column names, etc.).

* **Dynamic `optional`**: `optional` as `True/False` (static) works as expected, however dynamnic
expressions will be ignored for now. As a consequence, `hide_when_disabled` attribute is obsolete
until dynamic `optional` are supported again.

* **Attribute `count`**: we go back-and-forth with this one on bringing this one to the Cloud. In the meantime, switch back to non-dynamic elements, e.g. multiple dropdown, text input collecting list of values, etc.

* **Running `onecode-start`**: getting a local UI is in the works, it's a pretty big feature, thanks
for your patience on that one.


## :wave: Getting Help

If you are a OneCode customer, you may directly email our support team.
Feel free as well to browse the [GitHub Issues](https://github.com/deeplime-io/onecode/issues)
and reach out to the community by posting bug reports, questions and suggestions.
