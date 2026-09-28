from typing import Any, List

from onecode.utils.typing import is_type


def test_any_matches_every_value():
    assert is_type("x", Any)
    assert is_type(1, Any)


def test_unparameterized_list_matches_any_items():
    assert is_type([1, "a"], list)
    assert is_type([1, "a"], List)
    assert is_type([1, "a"], list[Any])
    assert not is_type("a", list[str])


def test_isinstance_failure_is_not_a_match():
    assert not is_type(1, "not-a-type")
