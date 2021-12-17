import pytest

from exomole.utils import load_dataframe_chunks
from .. import resources_path


def test_():
    import pathlib

    assert pathlib.Path(resources_path / "exomol_data" / "exomol.all").is_file()
