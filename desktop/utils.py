import re

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def _clean(line: str) -> str:
    return _ANSI_RE.sub("", line)


def _decode_line(line: bytes) -> str:
    try:
        return _clean(line.decode("utf-8").rstrip())
    except UnicodeDecodeError:
        try:
            return _clean(line.decode("gbk").rstrip())
        except UnicodeDecodeError:
            return _clean(line.decode("utf-8", errors="replace").rstrip())