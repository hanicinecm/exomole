import pytest

from exomole.exceptions import LineCommentError, LineValueError, LineWarning
from exomole.utils import parse_exomol_line


def test_line_consumption():
    lines = ["  val  #  comment  "] * 5
    parse_exomol_line(lines, 42, warn_on_comments=True)
    assert len(lines) == 4


def test_line_comment_error():
    lines = ["val", "val"]
    with pytest.raises(LineCommentError, match=r".*line 41.*"):
        parse_exomol_line(lines, 42, warn_on_comments=True)
    with pytest.raises(LineCommentError, match=r".*line 42.*foo.*"):
        parse_exomol_line(lines, 42, file_name="foo", warn_on_comments=True)


def test_line_value_error():
    lines = ["foo # foo", "poo # poo"]
    with pytest.raises(LineValueError, match=r".*Unexpected value type.*line 1.*"):
        parse_exomol_line(lines, 2, val_type=int, warn_on_comments=True)
    with pytest.raises(LineValueError, match=r".*Unexpected value type.*line 2.*"):
        parse_exomol_line(lines, 2, val_type=float, warn_on_comments=True)


def test_end_of_lines_value_error():
    lines = ["foo # foo", "poo # poo"]
    len_lines = len(lines)
    with pytest.raises(LineValueError, match="Run out of lines"):
        while True:
            parse_exomol_line(lines, len_lines, warn_on_comments=True)


def test_blank_line_warning():
    lines = ["       ", "first_val_after_blank # comment", "last_val # comment"]
    with pytest.warns(LineWarning, match=r".*Empty line.*line 1.*"):
        val = parse_exomol_line(lines, len(lines), warn_on_comments=True)
    assert val == "first_val_after_blank"


def test_unexpected_comment_not_warned():
    lines = ["val # real_comment"]
    num_lines = len(lines)
    with pytest.warns(None) as record:
        parse_exomol_line(
            lines,
            num_lines,
            expected_comment="expected_comment",
            warn_on_comments=False,
        )
    assert not record


def test_unexpected_comment_warned():
    lines = ["val # real_comment"]
    num_lines = len(lines)
    with pytest.warns(LineWarning, match=".*Unexpected comment.*line 1.*"):
        parse_exomol_line(
            lines, num_lines, expected_comment="expected_comment", warn_on_comments=True
        )


def test_value_type_cast():
    lines = ["1 # comment1", "2 # comment2", "3 # comment3", "4 # comment4"]
    num_lines = len(lines)
    assert (
        parse_exomol_line(lines, num_lines, expected_comment="comment1", val_type=int)
        == 1
    )
    assert (
        parse_exomol_line(lines, num_lines, expected_comment="comment2", val_type=float)
        == 2.0
    )
    assert (
        parse_exomol_line(lines, num_lines, expected_comment="comment3", val_type=str)
        == "3"
    )
    assert parse_exomol_line(lines, num_lines, expected_comment="comment4") == "4"
