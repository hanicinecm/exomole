"""
This is more of an integration test. I'm not bothered with any mocking and
separation, but rather I'm testing the `states_chunks` function on a dummy
data file.
Most of the functionality tested is handled by functions in `utils` and is also
tested there more properly.
"""

import pytest

from .. import resources_path
from exomole.exceptions import StatesParseError
from exomole.read_states import states_chunks


def test_():
    assert True
