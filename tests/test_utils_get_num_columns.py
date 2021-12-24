import pandas
import numpy as np
import pytest

import exomole.utils
from exomole.utils import get_num_columns


@pytest.mark.parametrize("df_shape", ((4, 3), (5, 1), (1, 5)))
def test_get_num_columns(monkeypatch, df_shape):
    r, c = df_shape

    def mock_load_dataframe_chunks(*_, **__):
        for _ in range(5):
            yield pandas.DataFrame(np.arange(r * c).reshape(df_shape))

    monkeypatch.setattr(
        exomole.utils, "load_dataframe_chunks", mock_load_dataframe_chunks
    )
    assert get_num_columns(file_path="mock_path") == c
