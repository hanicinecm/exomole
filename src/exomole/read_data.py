"""
TODO: add the module documentation
"""

from pathlib import Path

from .exceptions import DataParseError, StatesParseError, TransParseError
from .utils import load_dataframe_chunks, get_num_columns


def states_chunks(states_path, chunk_size, columns):
    """
    Get a generator of chunks of the dataset .states file.

    Generator of pandas.DataFrame chunks of the .states file, with
    rows indexed by the values of the first column in the .states file.

    The columns argument passed needs to contain names for *all* the columns
    *except the first* .states column, which is assumed to be the states index.

    The generated pandas.DataFrames are cast explicitly to dtype=str,
    to avoid possible nasty surprises caused by pandas guessing the types itself.
    The columns can be re-casted downstream to the more appropriate data types
    for faster processing. An example for the energy column might be as follows:
    state_chunk['E'] = state_chunk['col'].astype('float64')

    Parameters
    ----------
    states_path : str or Path
        Path to the .states file on the local file system.
    chunk_size : int
        Chunk size, should be chosen appropriately with regards to RAM size.
        Roughly 1_000_000 per 1GB consumed.
    columns : iterable of str
        Column names for all the columns in the states file except the first one,
        which is assumed to be the states index.
        Therefore, len(columns) must be one less than the number of actual columns
        in the .states file.

    Yields
    ------
    states_chunk : pandas.DataFrame
        Generated chunks of the states file, each is a pandas.DataFrame with columns
        according to the `columns` passed, and indexed by the values in the first
        column in the .states file.
        The whole dataframe is of string (object) data type.

    Raises
    ------
    StatesParseError
        If len(columns) inconsistent with the number of columns in the .states file.

    Examples
    --------
    >>> # TODO: Add an example.
    """
    try:
        chunks = load_dataframe_chunks(
            file_path=states_path,
            chunk_size=chunk_size,
            first_col_is_index=True,
            column_names=columns,
            dtype=str,
            check_num_columns=True,
        )
    except DataParseError as e:
        raise StatesParseError(str(e))
    for chunk in chunks:
        yield chunk


def trans_chunks(trans_paths, chunk_size):
    """
    Get a generator of chunks of the dataset .trans file.

    Generator of pd.DataFrame chunks of all the .trans files passed as the trans_paths
    argument.
    The columns are auto-named as "i", "f", "A_if" [, "v_if"]
    The "i" and "f" columns will correspond to the index of the DataFrames yielded by
    the read_states.states_chunks generator.
    No explicit data type casting is performed and pandas is trusted to correctly
    identify the "i" and "f" columns as "int64" and rest as "float64".

    Parameters
    ----------
    trans_paths : list of (str or Path)
        Paths to the .trans files on the local file system. They all need to belong to
        the same dataset, but no checks are made to assert that!
    chunk_size : int
        Chunk size, should be chosen appropriately with regards to RAM size, roughly
        10_000_000 per 1GB consumed.

    Yields
    ------
    trans_chunk : pd.DataFrame
        Generated chunks of all the .trans files, each is a pd.DataFrame with
        auto-named columns.

    Raises
    ------
    TransParseError
        If the first .trans file has number of columns other than {3, 4}.

    Examples
    --------
    >>> # TODO: Add an example.
    """
    trans_paths = sorted(trans_paths)

    num_cols = get_num_columns(trans_paths[0])
    columns = ["i", "f", "A_if"]
    if num_cols == 4:
        columns.append("v_if")
    elif num_cols != 3:
        raise TransParseError(
            f"Unexpected number of columns in {Path(trans_paths[0]).name}: {num_cols}"
        )
    assert num_cols in {3, 4}
    # yield all the chunks from all the files:
    for file_path in trans_paths:
        chunks = load_dataframe_chunks(
            file_path=file_path, chunk_size=chunk_size, column_names=columns
        )
        for chunk in chunks:
            yield chunk
