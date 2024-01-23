# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import List, Optional, Union

from onecode import RadioButton, convert_expr


class DynamicRadioButton(RadioButton):
    def __init__(
        self,
        key: str,
        value: Optional[Union[str, List[str]]],
        label: Optional[str] = None,
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        options: List[str] = [],
        horizontal: bool = False
    ):
        super().__init__(
            key,
            value,
            label,
            count,
            optional,
            hide_when_disabled,
            options=options,
            horizontal=horizontal
        )

    def _validate(
        self,
        value: str
    ) -> None:
        # cannot validate dynamic options
        if not isinstance(self.options, str) and value not in self.options:
            raise ValueError(f"[{self.key}] Not a valid choice: {value}")

    def streamlit(
        self,
        id: str
    ) -> str:
        key = self.key
        options_key = f'_options_{key}'
        default_key = f'_default_{key}'

        val = f"'''{self.value}'''" if isinstance(self.value, str) else self.value
        if isinstance(self.options, str):
            options = convert_expr(self.options)
        else:
            options = self.options

        return f"""
try:
    {options_key} = {options}
except:
    {options_key} = []

{default_key} = pydash.find_index({options_key}, lambda x: x == {val})
{default_key} = {default_key} if {default_key} >= 0 else 0

{key} = st.radio(
    {self.label},
    options={options_key},
    index={default_key},
    disabled={self.disabled},
    horizontal={self.horizontal},
    key={id}
)
"""
