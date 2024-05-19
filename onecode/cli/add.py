# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import os
import time

from InquirerPy import prompt
from InquirerPy.validator import PathValidator
from slugify import slugify
from yaspin import yaspin

from ..base.decorator import check_type
from ..base.enums import Env
from .utils import _add_flow, _get_flow_choices


@check_type
def add(
    project_path: str,
    name: str,
    before: str = None,
    cli: bool = True
) -> None:
    """
    Add a new flow to the given OneCode project.

    Args:
        project_path: Path to the root of the existing OneCode project.
        name: Name of the new flow to add.
        before: Insert the new flow before this flow id. Set it to None to put it in last position.
        cli: Set to False for no interaction.

    Raises:
        FileNotFoundError: if the project path is incorrect (i-e OneCode config file not found).

    """
    name = slugify(name, lowercase=False, separator=' ')

    with yaspin(text="Adding new flow") as spinner:
        try:
            if not os.path.exists(os.path.join(project_path, Env.ONECODE_CONFIG_FILE)):
                raise FileNotFoundError(
                    "Hmmm, it doesn't look like this is a OneCode project (config file not found)"
                )

            _add_flow(project_path, name, before)

            time.sleep(0.5 if cli else 0)
            spinner.text = f"Added {name} flow"
            spinner.ok("✅")

        except Exception as e:
            spinner.text = f"{e}"
            spinner.fail("💥 [Failed] -")

            if not cli:
                raise e


def main() -> None:    # pragma: no cover
    """
    Start a user-interactive CLI to add a new flow to an existing OneCode project.
    ```bash
    onecode-add
    ```

    """
    questions = [
        {
            "type": "confirm",
            "name": "proceed",
            "message": "Multi-steps are not yet available on OneCode Cloud, "
                       "would you like to continue anyway?",
            "default": False,
        },
        {
            "type": "filepath",
            "name": "project_path",
            "message": "Enter the path of the existing OneCode project",
            "default": os.getcwd(),
            "validate": PathValidator(is_dir=True, message="Input is not a directory"),
            "only_directories": True,
            "when": lambda result: result["proceed"],
        },
        {
            "type": "input",
            "name": "name",
            "message": "Enter the name of the new flow to add:",
            "validate": lambda result: len(result) > 0,
            "when": lambda result: result["proceed"],
        },
        {
            "type": "list",
            "name": "before",
            "message": "Choose before which flow:",
            "choices": lambda result: _get_flow_choices(result['project_path']),
            "default": None,
            "when": lambda result: result["proceed"],
        }
    ]

    result = prompt(questions)
    if result['proceed']:
        add(result['project_path'], result['name'], result['before'])
