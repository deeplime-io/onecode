from onecode import Keyword, convert_expr, indent_block


def test_convert_expr():
    # test for a None expression
    assert convert_expr(None) is None

    # test for a valid expression
    assert convert_expr("2 * $test expression$ + 1") == \
        f'2 * {Keyword.DATA}["test_expression"] + 1'


def test_indent_block():
    # test for a string
    assert indent_block("test") == '    test'
    assert indent_block("test", indent=8) == '        test'

    # test for a list of strings
    assert indent_block(["test1\n", "test2"]) == '    test1\n    test2'
