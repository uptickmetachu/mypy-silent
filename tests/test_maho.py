import re
from typing import Optional, Set

import pytest

from mypy_silent.maho import add_type_ignore_comment, remove_type_ignore_comment

_type_ignore_re = re.compile(r"# type: ignore(\[(?P<error_code>[a-z, \-]+)\])?")


@pytest.mark.parametrize(
    "input,error_code,output",
    (
        (
            "        host, port, protocol = m.groups()\r\n",
            None,
            "        host, port, protocol = m.groups()  # type: ignore\r\n",
        ),
        (
            "        host, port, protocol = m.groups()\r\n",
            "misc",
            "        host, port, protocol = m.groups()  # type: ignore[misc]\r\n",
        ),
        ("print(a(2, 's'))  # noqa", None, "print(a(2, 's'))  # type: ignore # noqa"),
        (
            "print(a(2, 's'))  # noqa",
            "misc",
            "print(a(2, 's'))  # type: ignore[misc] # noqa",
        ),
    ),
)
def test_add_type_ignore_comment(
    input: str, error_code: Optional[str], output: str
) -> None:
    assert add_type_ignore_comment(input, error_code=error_code) == output


@pytest.mark.parametrize(
    "input,output",
    (
        (
            "        host, port, protocol = m.groups()  # type: ignore\r\n",
            "        host, port, protocol = m.groups()\r\n",
        ),
        (
            "        host, port, protocol = m.groups()  # type: ignore[misc]\r\n",
            "        host, port, protocol = m.groups()\r\n",
        ),
        ("# type: ignore. very good", "#. very good"),
        ("# type: ignore[misc]. very good", "#. very good"),
        ("# type: ignore[misc, arg-type]. very good", "#. very good"),
    ),
)
def test_remove_type_ignore_comment(input: str, output: str) -> None:
    assert remove_type_ignore_comment(input) == output


def test_add_type_ignore_with_existing_comment() -> None:
    input = "host, port, protocol = m.groups()  # type: ignore\r\n"

    assert (
        add_type_ignore_comment(input, error_code=None)
        == "host, port, protocol = m.groups()  # type: ignore\r\n"
    )
    assert (
        add_type_ignore_comment(input, error_code="arg-type")
        == "host, port, protocol = m.groups()  # type: ignore[arg-type]\r\n"
    )


def test_add_type_ignore_with_existing_comment_with_code() -> None:
    input = "host, port, protocol = m.groups()  # type: ignore[misc]\r\n"

    assert (
        add_type_ignore_comment(input, error_code="arg-type")
        == "host, port, protocol = m.groups()  # type: ignore[arg-type, misc]\r\n"
    )
    assert (
        add_type_ignore_comment(input, error_code=None)
        == "host, port, protocol = m.groups()  # type: ignore[misc]\r\n"
    )


def test_add_type_ignore_with_fmt_skip() -> None:
    input = "host, port, protocol = m.groups()"

    assert (
        add_type_ignore_comment(input, error_code=None, nofmt=True)
        == "host, port, protocol = m.groups()  # type: ignore # fmt: skip"
    )

    assert (
        add_type_ignore_comment(input, error_code=None, nofmt=True)
        == "host, port, protocol = m.groups()  # type: ignore # fmt: skip"
    )


def test_add_type_ignore_with_fmt_skip_to_line_already_with_fmt_skip() -> None:
    input = "host, port, protocol = m.groups() # fmt: skip"

    assert (
        add_type_ignore_comment(input, error_code=None, nofmt=True)
        == "host, port, protocol = m.groups()  # type: ignore # fmt: skip"
    )
