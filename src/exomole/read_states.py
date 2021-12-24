"""
TODO: add the module documentation
"""

from pathlib import Path

from .exceptions import DataParseError, StatesParseError
from .utils import load_dataframe_chunks


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
