import requests
import warnings

import pandas as pd

from .exceptions import APIError, LineWarning, LineCommentError, LineValueError


def get_file_raw_text(
    which, molecule_slug=None, isotopologue_slug=None, dataset_name=None
):
    """Get the raw text of an ExoMol file.

    Get the raw text of an exomol .def or .all file.
    The file is requested over https under the relevant URL via the ExoMol public API.
    The 'which' argument determined if the .def file or the .all file is requested.
    All the other arguments are ignored for which='all' and do not need to be passed.

    Parameters
    ----------
    which : str
        Out of {'all', 'def'}
    molecule_slug, isotopologue_slug, dataset_name : str or None
        Optional, ignored if which == 'all'.

    Returns
    -------
    raw_text : str
        The raw text of the file requested.

    Raises
    ------
    APIError
        If the arguments passed result in a request with an unsuccessful response.
    """
    base_url = "https://www.exomol.com/db/"
    if which == "all":
        url = f"{base_url}/exomol.all"
    elif which == "def" and all([molecule_slug, isotopologue_slug, dataset_name]):
        url = (
            f"{base_url}{molecule_slug}/{isotopologue_slug}/"
            f"{dataset_name}/{isotopologue_slug}__{dataset_name}.def"
        )
    else:
        raise ValueError(f"Unrecognised arguments passed")

    response = requests.get(url)
    if response.status_code != 200:
        raise APIError(f"Unsuccessful response received from {url}")
    raw_text = response.text
    return raw_text


def parse_exomol_line(
    lines,
    n_orig,
    expected_comment=None,
    file_name=None,
    val_type=None,
    warn_on_comments=False,
):
    """Line parser for the ExoMol files (.all and .def).

    List of the file lines is passed as well as the original length of the list.
    The top line of lines is popped (lines gets changed as an externality) and the
    line value is extracted and returned.
    The list of lines is therefore being consumed line by line with each call of this
    function.
    If the expected_comment is passed, the comment in the top line (after # symbol)
    is asserted to equal the expected_comment.
    If the comment does not match and warn_on_comments is True, a the LineCommentWarning
    is raised.

    Parameters
    ----------
    lines : list of str
        List at first containing all the lines of the file which are then being
        popped one by one.
    n_orig : int
        The number of lines of the full file (for error raising only).
    expected_comment : str or None
        The comment after the # symbol on each line is expected to match the
        passed expected comment.
    file_name : str or None
        The name of the file that lines belonged to (for error raising only).
    val_type : type or None
        The intended type of the parsed value, the value will be converted to.
    warn_on_comments : bool or None
        If True, warning will be raised if the parsed comment does not match the
        expected comment.

    Returns
    -------
    str | int | float
        Value belonging to the top line in lines passed. Type is either str, or passed
        val_type.

    Raises
    ------
    LineCommentError
        If the top line does not have the required format of value # comment
    LineValueError
        If the value parsed from the top line cannot be converted to the val_type.

    Warnings
    --------
    LineWarning
        If warn_on_comment set to True and the comment parsed from the top line
        does not match the expected_comment passed, the LineWarning is raised.
        Also raised if an empty line is detected anywhere.
    """

    while True:
        try:
            line = lines.pop(0).strip()
        except IndexError:
            msg = f"Run out of lines"
            if file_name:
                msg += f" in {file_name}"
            raise LineValueError(msg)
        line_num = n_orig - len(lines)
        if line:
            break
        else:
            msg = f"Empty line detected on line {line_num}"
            if file_name:
                msg += f" in {file_name}"
            warnings.warn(msg, LineWarning)
    try:
        val, comment = line.split("# ")
        val = val.strip()
    except ValueError:
        msg = f"Unexpected line format detected on line {line_num}"
        if file_name:
            msg += f" in {file_name}"
        raise LineCommentError(msg)
    if val_type:
        try:
            val = val_type(val)
        except ValueError:
            msg = f"Unexpected value type detected on line {line_num}"
            if file_name:
                msg += f" in {file_name}"
            raise LineValueError(msg)
    if comment != expected_comment and warn_on_comments:
        msg = f"Unexpected comment detected on line {line_num}!"
        if file_name:
            msg += f" in {file_name}"
        warnings.warn(msg, LineWarning)
    return val


def load_dataframe_chunks(
    file_path, chunk_size, column_names=None, index_col=None, dtype=None
):
    """
    Loads chunks of either .states.bz2 file or .trans.bz2 file from the local file
    system with the specified chunk size.

    Parameters
    ----------
    file_path : str or Path
        Path to the file I want to load in - either .states or .trans file (bz2).
    chunk_size : int
        Appropriate value depends on RAM
    column_names : list of str or None
        Optional column names of the file loaded. If the index_column is passed and > 1,
        the column_names are without the index column.
    index_col : int or None
        Optional index column number, None by default.
    dtype : type or None
        Optional data type to cast to pd.read_csv

    Returns
    -------
    df_chunks : pandas.io.parsers.TextFileReader
        chunks of the read pd.DataFrame. Access by `for chunk in df_chunks: ...`, where
        each chunk is a pd.DataFrame.
    """
    df_chunks = pd.read_csv(
        file_path,
        compression="bz2",
        sep=r"\s+",
        header=None,
        index_col=index_col,
        names=column_names,
        chunksize=chunk_size,
        iterator=True,
        low_memory=False,
        dtype=dtype,
    )
    return df_chunks


def get_num_columns(file_path):
    """
    Gets the number of columns in the .bz2 compressed either .states or .trans file
    under the file_path.

    Parameters
    ----------
    file_path : str or Path

    Returns
    -------
    int
    """
    for chunk in load_dataframe_chunks(file_path, chunk_size=1):
        _, num_cols = chunk.shape
        return int(num_cols)


class DataClass:
    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            setattr(self, attr, val)

    def __repr__(self):
        cls_name = self.__class__.__name__
        attrs_str = ", ".join(f"{attr}={val}" for attr, val in vars(self).items())
        return f"{cls_name}({attrs_str})"
