"""
This is more of an integration test. I'm not bothered with any mocking and
separation, but rather I'm testing the `trans_chunks` function on some dummy
data files.
Most of the functionality tested is handled by functions in `utils` and is also
tested there more properly.
"""

import pytest

import exomole
from exomole.exceptions import TransParseError
from exomole.read_trans import trans_chunks
from .. import resources_path

dummy_trans_paths = list(
    resources_path.glob("dummy_trans_5x4_int_int_float_float.trans*.bz2")
)
assert len(dummy_trans_paths) == 3


@pytest.mark.parametrize("num_trans_cols", (1, 2, 5, 6, 7))
def test_too_many_columns(num_trans_cols, monkeypatch):
    monkeypatch.setattr(exomole.read_trans, "get_num_columns", lambda x: num_trans_cols)
    with pytest.raises(TransParseError):
        list(trans_chunks(dummy_trans_paths, 5))


@pytest.mark.parametrize(
    "trans_path, cols",
    (
        (
            resources_path / "dummy_trans_5x3_int_int_float.trans.bz2",
            "i f A_if".split(),
        ),
        (
            resources_path / "dummy_trans_5x4_int_int_float_float.trans01.bz2",
            "i f A_if v_if".split(),
        ),
    ),
)
def test_columns(trans_path, cols):
    for chunk in trans_chunks([trans_path], 1):
        assert list(chunk.columns) == cols


@pytest.mark.parametrize(
    "chunk_size, num_chunks", ((1, 15), (2, 9), (3, 6), (4, 6), (5, 3), (100, 3))
)
def test_chunk_size(chunk_size, num_chunks):
    assert len(list(trans_chunks(dummy_trans_paths, chunk_size))) == num_chunks


@pytest.mark.parametrize(
    "col, dtype",
    (("i", "int64"), ("f", "int64"), ("A_if", "float64"), ("v_if", "float64")),
)
def test_dtype_cast(col, dtype):
    """Hopefully the types are correctly cast as int, int, float, float"""
    for chunk in trans_chunks(dummy_trans_paths, 5):
        assert chunk[col].dtype == dtype
