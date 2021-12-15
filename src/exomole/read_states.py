from pathlib import Path

from .exceptions import StatesParseError
from .utils import load_dataframe_chunks, get_num_columns


def states_chunks(states_path, chunk_size, columns):
    """
    Get a generator of chunks of the dataset .states file.

    Generator of pd.DataFrame chunks of the .states file, with
    rows indexed by the values of the first column in the .states file.
    The columns argument passed needs to contain names for *all* the columns
    *except the first* .states column, which is assumed to be the states index.
    The generated DataFrames are cast explicitly to dtype=str, to avoid possible
    nasty surprises caused by pandas guessing the types itself.
    The columns can be re-casted downstream to the more appropriate data types
    for faster processing. An example for the energy column is as follows:
    state_chunk['E'] = state_chunk['col'].astype('float64')

    Parameters
    ----------
    states_path : str or Path
        Path to the .states file on the local file system.
    chunk_size : int
        Chunk size, should be chosen appropriately with regards to RAM size.
        Roughly 1_000_000 per 1GB consumed
    columns : list of str
        Column names for all the columns in the states file except the first one,
        which is assumed to be the states index.
        Therefore, len(columns) must be one less than the number of actual columns
        in the .states file.

    Yields
    ------
    states_chunk : pd.DataFrame
        Generated chunks of the states file, each is a pd.DataFrame with columns
        according to the argument passed, and indexed by the values in the first
        column in .states file.
        The whole dataframe is of string type.

    Raises
    ------
    StatesParseError
        If len(columns) inconsistent with the number of columns in the .states file.
    """
    states_path = Path(states_path)
    num_cols = get_num_columns(states_path)
    if num_cols != len(columns) + 1:
        raise StatesParseError(
            f"{len(columns)} column names passed, while "
            f"{states_path.name} only {num_cols - 1} columns "
            f"(excluding the index column)."
        )
    chunks = load_dataframe_chunks(
        file_path=states_path,
        chunk_size=chunk_size,
        column_names=columns,
        index_col=0,
        dtype=str,
    )
    for chunk in chunks:
        if list(chunk.columns) != columns[1:]:
            raise StatesParseError(f"Defense: {states_path}")
        yield chunk
