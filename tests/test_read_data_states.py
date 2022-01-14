"""
This is more of an integration test. I'm not bothered with any mocking and
separation, but rather I'm testing the `states_chunks` function on a dummy
data file.
Most of the functionality tested is handled by functions in `utils` and is also
tested there more properly.
"""

import pytest

from exomole.exceptions import StatesParseError
from exomole.read_data import states_chunks
from . import resources_path

dummy_states_path = resources_path.joinpath(
    "dummy_states_10x5_int_float_int_str_int.states.bz2"
)
assert dummy_states_path.is_file()


def test_inconsistent_columns():
    with pytest.raises(StatesParseError):
        # too many columns:
        list(
            states_chunks(
                dummy_states_path, chunk_size=10, columns="i a b c d e".split()
            )
        )
    with pytest.raises(StatesParseError):
        # too little columns:
        list(states_chunks(dummy_states_path, chunk_size=10, columns="i a b c".split()))


def test_consistent_columns():
    columns = "i a b c d".split()
    for chunk in states_chunks(dummy_states_path, chunk_size=1, columns=columns):
        assert list(chunk.columns) == "a b c d".split()


@pytest.mark.parametrize(
    "chunk_size, num_chunks", ((1, 10), (2, 5), (3, 4), (5, 2), (10, 1), (100, 1))
)
def test_chunk_size(chunk_size, num_chunks):
    columns = "i a b c d".split()
    assert (
        len(list(states_chunks(dummy_states_path, chunk_size, columns))) == num_chunks
    )


@pytest.mark.parametrize("col", "a b c d".split())
def test_dtype_cast(col):
    dtype = "O"
    columns = "i a b c d".split()
    for chunk in states_chunks(dummy_states_path, 2, columns):
        assert chunk[col].dtype == dtype


def test_index_dtype():
    dtype = "int64"
    columns = "i a b c d".split()
    for chunk in states_chunks(dummy_states_path, 2, columns):
        assert chunk.index.dtype == dtype


def test_incompatible_columns():
    with pytest.raises(StatesParseError):
        for _ in states_chunks(dummy_states_path, 2, columns="foo a b c d".split()):
            pass