import pytest

from exomole.exceptions import APIError
from exomole.utils import get_file_raw_text_over_api


def test_which():
    with pytest.raises(ValueError):
        get_file_raw_text_over_api(which="foo")


@pytest.mark.parametrize("api_inputs", [[], ["foo"], ["foo", "ham"]])
def test_args(api_inputs):
    with pytest.raises(ValueError):
        get_file_raw_text_over_api("def", *api_inputs)


def test_invalid_response():
    with pytest.raises(APIError):
        get_file_raw_text_over_api("def", "foo", "ham", "spam")


def test_valid_response_all():
    raw_text = get_file_raw_text_over_api("all")
    assert type(raw_text) is str
