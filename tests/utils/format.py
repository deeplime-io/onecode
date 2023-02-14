import re


def strip(msg: str) -> str:
    return re.sub("\n+", "", re.sub(" +", " ", msg.strip().strip("\n")))
