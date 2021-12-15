from pathlib import Path

from .exceptions import StatesParseError
from .utils import load_dataframe_chunks


def states_chunks(states_path, chunk_size, columns):
    """
    Get a generator of chunks of the dataset .states file.

    Generator of pd.DataFrame chunks of the .states file, with
    (hopefully correctly) assigned columns, and indexed by states indices
    (the states indices are NOT present as a column, but as the dataframe index).
    The columns of each chunk are as follows:
    'E', 'g_tot', 'J' [, 'tau', 'g_J'], '<q_1>' [, '<q_2>', ..., '<q_N>']

    Parameters
    ----------
    states_path : str or Path
        Path to the .states file on the local file system.
    chunk_size : int
        Chunk size, should be chosen appropriately with regards to RAM size.
    columns : list of str
        Column names for all the columns in the states file. The first columns will
        be the DataFrame index and must not be passed. Therefore, len(columns) must
        be one less than the number of actual columns in the .states file.

    Yields
    -------
    states_chunk : pd.DataFrame
        Generated chunks of the states file, each is a pd.DataFrame with columns
        according to the argument passed, and indexed by the values in the first
        column in .states file.
    """
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
        chunk.loc[:, "J"] = chunk.loc[:, "J"].astype("float64")
        chunk.loc[:, "E"] = chunk.loc[:, "E"].astype("float64")
        chunk.loc[:, "g_tot"] = chunk.loc[:, "g_tot"].astype("float64")
        yield chunk
