import re
from typing import List, Optional, Union

from slugify import slugify

from ..base.decorator import check_type
from ..base.enums import Keyword


@check_type
def convert_expr(expr: Optional[str]) -> str:
    """
    Replace instances of a pattern in a given expression with a keyword and slugified values.

    Parameters:
        expr: The expression to be converted.

    Returns:
        The converted expression.

    """
    if expr is None:
        return None

    def replace(match):
        return f'''{Keyword.DATA}["{slugify(match.group(), separator='_')}"]'''

    pattern = re.compile(r'\$(.*?)\$')
    return pattern.sub(replace, expr)


@check_type
def indent_block(
    code: Union[str, List[str]],
    indent: int = 4
) -> str:
    """
    Indent a code block by a given number of spaces.

    Parameters:
        code: The code block to be indented.
        indent: The number of spaces to be indented.

    Returns:
        The indented code block.

    """
    line = ''.ljust(indent) + ''.join(code)
    return f"\n{''.ljust(indent)}".join(line.split('\n'))
