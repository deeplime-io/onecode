from typing import Any, List

from onecode import InputElement


class InvalidElem(InputElement):
    def __init__(
        self,
        key: str,
        value: str,
        label: str,
        extra: int
    ):
        super().__init__(key, value, label, extra=extra)

    @property
    def _value_type(self) -> type:
        return str

    @staticmethod
    def imports() -> List[str]:
        def f():
            pass
        return f

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
