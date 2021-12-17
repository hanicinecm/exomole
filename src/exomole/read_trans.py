"""
TODO: add the module documentation
"""

from pathlib import Path

from .exceptions import TransParseError
from .utils import load_dataframe_chunks, get_num_columns


def trans_chunks(trans_paths, chunk_size):
    """
    Get a generator of chunks of the dataset .trans file.

    Generator of pd.DataFrame chunks of all the .trans passed as the trans_paths
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
        Generated chunks of the .trans file, each is a pd.DataFrame with auto-named
        columns.

    Raises
    ------
    TransParseError
        If the first .trans file has number of columns other than {3, 4}.

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
    # yield all the chunks from all the files:
    for file_path in trans_paths:
        chunks = load_dataframe_chunks(
            file_path=file_path, chunk_size=chunk_size, column_names=columns
        )
        for chunk in chunks:
            yield chunk
