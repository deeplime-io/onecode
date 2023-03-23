# SPDX-FileCopyrightText: 2023 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

from typing import Dict, List, Optional, Union

import pydash

from onecode import InputElement


class NeuralNetInput(InputElement):
    def __init__(
        self,
        key: str,
        value: Optional[Dict],
        count: Optional[Union[int, str]] = None,
        optional: Union[bool, str] = False,
        hide_when_disabled: bool = False,
        options: Union[List, str] = [],
        multiple: bool = False
    ):
        super().__init__(
            key=key,
            value=value,
            count=count,
            optional=optional,
            hide_when_disabled=hide_when_disabled,
            options=options,
            multiple=multiple
        )

    @property
    def _value_type(self) -> type:
        return Dict

    def _validate(
        self,
        value: Dict
    ) -> None:
        neurons = value.get("neurons")
        activation = value.get("activation")
        dropout = value.get("dropout")

        if neurons <= 0:
            raise ValueError(f"Number of neurons cannot be negative: {neurons}")

        elif activation not in ["tanh", "sigmoid", "relu"]:
            raise ValueError(f"Invalid activation function: {activation}")

        elif dropout < 0 or dropout > 1:
            raise ValueError(f"Dropout must be in range [0, 1]: {dropout}")

    def streamlit(
        self,
        id: str
    ) -> str:
        key = self.key
        value = self.value
        count = self.count

        options_key = f'options_{key}'
        default_key = f'default_{key}'
        option_id = f'option_{key}'
        option_val = f'val_{key}'

        options = [
            'relu',
            'sigmoid',
            'tanh',
        ]

        return f"""
{options_key} = {options}
if {count} is not None:
    {option_id} = int({id}.split('_')[-1])
else:
    {option_id} = 0
{option_val} = pydash.get({value}, [{option_id}, 'activation'], 'tanh')
{default_key} = pydash.find_index({options_key}, lambda x: x == {option_val})
{default_key} = {default_key} if {default_key} >= 0 else 0

# NeuralNetInput {key}
left_{key}, mid_{key}, right_{key} = st.columns(3)
neurons_{key} = left_{key}.slider(
    'Neurons',
    value=pydash.get({value}, [{option_id}, 'neurons'], 16),
    min_value=8,
    max_value=64,
    step=1,
    key='neuron_' + {id}
)

activation_{key} = mid_{key}.selectbox(
    'Activation',
    index={default_key},
    options={options_key},
    disabled={self.disabled},
    key='activation_' + {id}
)

dropout_{key} = right_{key}.slider(
    'Dropout',
    value=pydash.get({value}, [{option_id}, 'dropout'], 0.),
    min_value=0.,
    max_value=0.9,
    key='dropout' + {id}
)

{key} = {{
    "neurons": neurons_{key},
    "activation": activation_{key},
    "dropout": dropout_{key}
}}
"""
