# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
import shutil
import stat
import subprocess
import time

from InquirerPy import prompt
from InquirerPy.validator import PathValidator
from slugify import slugify
from yaspin import yaspin

from ..base.decorator import check_type
from .utils import _add_flow


@check_type
def create(
    project_path: str,
    name: str,
    main_flow_name: str = None,
    cli: bool = True
) -> None:
    """
    Create a new OneCode project.

    Args:
        project_path: Path to the folder where to put the new OneCode project.
        name: Name of the new OneCode project.
        main_flow_name: Name of the main flow: if None, it will be constructed from the name of
            the OneCode project.
        cli: Set to False for no interaction.

    Raises:
        FileExistsError: if the project path already exists.

    """
    folder_name = slugify(name, lowercase=False, separator='_')
    project_path = os.path.join(project_path, folder_name)

    with yaspin(text="Creating new OneCode project") as spinner:
        try:
            if os.path.exists(project_path):
                raise FileExistsError(
                    f'A file or a directory with the path {project_path} already exists'
                )

            shutil.copytree(os.path.join(os.path.dirname(__file__), 'skeleton'), project_path)
            _add_flow(project_path, name if main_flow_name is None else main_flow_name)
            try:
                process = subprocess.run(['git', 'init'], cwd=project_path, capture_output=True)
                err = process.stderr.decode()
                if err:   # pragma: no cover
                    raise SystemError(err)

                print(f'\n{process.stdout.decode()}')

                precommit_hook = os.path.join(project_path, '.git', 'hooks', 'pre-commit')
                with open(precommit_hook, 'w') as f:
                    f.write("""#!/bin/bash

extract=$(onecode-extract data/parameters.json)
if [[ "$extract" != *"Parameters extracted to data/parameters.json"* ]]
then
  echo "Error extracting parameters"
  exit 1
fi

echo "OneCode parameters extracted and auto-committed"
exec git add data/parameters.json
""")
                # chmod +x required
                st = os.stat(precommit_hook)
                os.chmod(precommit_hook, st.st_mode | stat.S_IEXEC)

            except Exception:   # pragma: no cover
                print('\nWarning: Git not properly initialized')

            time.sleep(1 if cli else 0)
            spinner.text = f"Created {name} OneCode project"
            spinner.ok("✅")

        except Exception as e:
            spinner.text = f"{e}"
            spinner.fail("💥 [Failed] -")

            if not cli:
                raise e


def main() -> None:    # pragma: no cover
    """
    Start a user-interactive CLI to create a new OneCode project.
    ```bash
    onecode-create
    ```

    """
    questions = [
        {
            "type": "filepath",
            "name": "project_path",
            "message": "Enter the path where to create OneCode project",
            "default": os.getcwd(),
            "validate": PathValidator(is_dir=True, message="Input is not a directory"),
            "only_directories": True,
        },
        {
            "type": "input",
            "name": "name",
            "message": "Enter your OneCode project name:",
            "validate": lambda result: len(result) > 0
        },
        {
            "type": "input",
            "name": "flow_name",
            "message": "Pick a name for your main flow:",
            "validate": lambda result: len(result) > 0,
            "default": lambda answers: answers['name']
        }
    ]

    result = prompt(questions)
    create(result['project_path'], result['name'], result['flow_name'])
