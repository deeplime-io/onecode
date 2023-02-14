from typing import Any

from onecode import InputElement


class EmptyInput(InputElement):
    def __init__(
        self,
        key: str
    ):
        super().__init__(
            key,
            value=None,
            optional=True
        )

    @property
    def _value_type(self) -> type:
        return Any

    def streamlit(
        self,
        id: str
    ) -> str:
        pass

    def _validate(
        self,
        value: Any
    ) -> None:
        pass
