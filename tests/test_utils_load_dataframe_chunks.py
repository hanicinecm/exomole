import re

import pytest

import exomole
from exomole.utils import load_dataframe_chunks, DataParseError
from . import resources_path


data_path = resources_path / "dummy_data_5x5_int.bz2"


@pytest.mark.parametrize("chunk_size, num_chunks", ((1, 5), (2, 3), (5, 1), (50, 1)))
def test_number_of_chunks(chunk_size, num_chunks, monkeypatch):
    monkeypatch.setattr(exomole.utils, "get_num_columns", lambda x: 5)
    chunks = list(load_dataframe_chunks(data_path, chunk_size=chunk_size))
    assert len(chunks) == num_chunks
    assert len(chunks[0]) == min(chunk_size, 5)

    chunks = list(
        load_dataframe_chunks(
            data_path,
            chunk_size=chunk_size,
            first_col_is_index=True,
            column_names="a b c d".split(),
        )
    )
    assert len(chunks) == num_chunks
    assert len(chunks[0]) == min(chunk_size, 5)


def test_chunks_datatypes(monkeypatch):
    monkeypatch.setattr(exomole.utils, "get_num_columns", lambda x: 5)
    for chunk in load_dataframe_chunks(data_path, 1):
        # dtype determined by pandas, hopefully as int
        assert chunk.values.dtype == "int64"
        break
    for chunk in load_dataframe_chunks(data_path, 5, dtype=str):
        assert chunk.values.dtype == "O"
    for chunk in load_dataframe_chunks(data_path, 5, dtype=float):
        assert chunk.values.dtype == "float64"
    for chunk in load_dataframe_chunks(data_path, 5, dtype=int):
        assert chunk.values.dtype == "int64"


def test_too_many_columns(monkeypatch):
    monkeypatch.setattr(exomole.utils, "get_num_columns", lambda x: 5)
    with pytest.raises(
        DataParseError,
        match=re.escape(
            "dummy_data_5x5_int.bz2 has 5 columns, "
            "but columns ['a', 'b', 'c', 'd'] passed."
        ),
    ):
        for _ in load_dataframe_chunks(data_path, 1, column_names="a b c d".split()):
            pass

    with pytest.raises(
        DataParseError,
        match=re.escape(
            "dummy_data_5x5_int.bz2 has 5 columns, "
            "but index + columns ['a', 'b', 'c'] passed."
        ),
    ):
        for _ in load_dataframe_chunks(
            data_path, 1, first_col_is_index=True, column_names="a b c".split()
        ):
            pass


def test_not_enough_columns(monkeypatch):
    monkeypatch.setattr(exomole.utils, "get_num_columns", lambda x: 5)
    with pytest.raises(
        DataParseError,
        match=re.escape(
            f"dummy_data_5x5_int.bz2 has 5 columns, "
            f"but columns ['a', 'b', 'c', 'd', 'e', 'f'] passed."
        ),
    ):
        for _ in load_dataframe_chunks(
            data_path, 1, column_names="a b c d e f".split(), check_num_columns=True
        ):
            pass

    with pytest.raises(
        DataParseError,
        match=re.escape(
            f"dummy_data_5x5_int.bz2 has 5 columns, "
            f"but index + columns ['a', 'b', 'c', 'd', 'e'] passed."
        ),
    ):
        for _ in load_dataframe_chunks(
            data_path,
            1,
            first_col_is_index=True,
            column_names="a b c d e".split(),
            check_num_columns=True,
        ):
            pass


def test_column_names_no_index(monkeypatch):
    monkeypatch.setattr(exomole.utils, "get_num_columns", lambda x: 5)
    column_names = "a b c d e".split()
    for chunk in load_dataframe_chunks(
        data_path, 1, column_names=column_names, check_num_columns=True
    ):
        assert list(chunk.columns) == column_names


def test_column_names_with_index(monkeypatch):
    monkeypatch.setattr(exomole.utils, "get_num_columns", lambda x: 5)
    column_names = "a b c d".split()
    for chunk in load_dataframe_chunks(
        data_path,
        1,
        first_col_is_index=True,
        column_names=column_names,
        check_num_columns=True,
    ):
        assert list(chunk.columns) == column_names


def test_load_data_no_index(monkeypatch):
    monkeypatch.setattr(exomole.utils, "get_num_columns", lambda x: 5)
    for chunk in load_dataframe_chunks(
        data_path,
        5,
        first_col_is_index=False,
        column_names="a b c d e".split(),
        check_num_columns=True,
        dtype=float,
    ):
        assert list(chunk.columns) == "a b c d e".split()
        assert list(chunk.index) == [0, 1, 2, 3, 4]
        assert str(chunk.loc[4, "e"]) == "24.0"
        assert chunk.shape == (5, 5)


def test_load_data_with_index(monkeypatch):
    monkeypatch.setattr(exomole.utils, "get_num_columns", lambda x: 5)
    for i, chunk in enumerate(
        load_dataframe_chunks(
            data_path,
            1,
            first_col_is_index=True,
            column_names="a b c d".split(),
            check_num_columns=True,
            dtype=float,
        )
    ):
        assert list(chunk.columns) == "a b c d".split()
        assert list(chunk.index) == [int(i * 5)]
        assert chunk.shape == (1, 4)


def test_load_data_with_index_no_columns(monkeypatch):
    monkeypatch.setattr(exomole.utils, "get_num_columns", lambda x: 5)
    for chunk in load_dataframe_chunks(
        data_path, 5, first_col_is_index=True, dtype=int
    ):
        assert list(chunk.columns) == [1, 2, 3, 4]
        assert list(chunk.index) == [0, 5, 10, 15, 20]
        assert str(chunk.loc[20, 4]) == "24"
        assert chunk.shape == (5, 4)
