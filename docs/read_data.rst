************************************
Reading the .states and .trans files
************************************

The ``exomole.read_data`` module contains two stand-alone functions for reading the
datasets' *states* and *trans* files in chunks as ``pandas.DataFrame`` instances.

Those two are ``states_chunks`` and ``trans_chunks``. Both functions take paths to the
data files as the first argument and can handle both ``*.bz2`` - compressed files, as
well as uncompressed files. Both functions then return *generators*, which yield
chunks of the data as ``DataFrame`` instances.

The next two sections show pretty self-explanatory use examples of both data-readout
generators in use:


Examples of ``states_chunks`` usage:
====================================

.. code-block:: pycon

    >>> from pathlib import Path
    >>> from exomole.read_data import states_chunks

    >>> # replace the following with the real data directory path:
    >>> exomol_data_dir = Path("tests/resources/exomol_data")

    >>> # let us take the following dataset as an example:
    >>> dataset_dir = exomol_data_dir / "CO" / "12C-16O" / "Li2015"

    >>> states_path = dataset_dir / "12C-16O__Li2015.states.bz2"

The ``states_chunks`` generator expects (apart from the ``states_path`` argument) also
the column labels of the *states* file data table. This must either be known, or
extracted from the ``*.def`` file belonging to the same dataset:

.. code-block:: pycon

    >>> from exomole.read_def import DefParser

    >>> def_path = dataset_dir / "12C-16O__Li2015.def"

    >>> def_parser = DefParser(path=def_path)
    >>> def_parser.parse(warn_on_comments=False)

    >>> columns = def_parser.get_states_header()

    >>> columns
    ['i', 'E', 'g_tot', 'J', 'v', 'kp']

Now, the ``states_chunks`` generator can be called and the data read. The default chunk
size it set to 1,000,000 rows:

.. code-block:: pycon

    >>> for dataframe in states_chunks(states_path=states_path, columns=columns):
    ...     print(dataframe)
                     E g_tot    J   v kp
    1         0.000000     1    0   0  e
    2      2143.271100     1    0   1  e
    3      4260.062200     1    0   2  e
    4      6350.439100     1    0   3  e
    5      8414.469300     1    0   4  e
    ...
    6379  87147.136100   303  151  36  e
    6380  87937.894700   303  151  37  e
    6381  88698.357100   303  151  38  e
    6382  89427.550400   303  151  39  e
    6383  90124.333200   303  151  40  e
    ...
    [6383 rows x 5 columns]

In this case, the actual number of rows in the file is way less than the set chunk size,
so only one dataframe is yielded. Let us try decreasing the chunk size:

.. code-block:: pycon

    >>> for dataframe in states_chunks(states_path, columns, chunk_size=5000):
    ...     print(dataframe)
                     E g_tot    J   v kp
    1         0.000000     1    0   0  e
    2      2143.271100     1    0   1  e
    3      4260.062200     1    0   2  e
    4      6350.439100     1    0   3  e
    5      8414.469300     1    0   4  e
    ...
    4996  80725.299500   237  118  39  e
    4997  81623.628000   237  118  40  e
    4998  82494.861900   237  118  41  e
    4999  26220.858500   239  119   0  e
    5000  28113.857800   239  119   1  e
    ...
    [5000 rows x 5 columns]
                     E g_tot    J   v kp
    5001  29980.317300   239  119   2  e
    5002  31820.305600   239  119   3  e
    5003  33633.893000   239  119   4  e
    5004  35421.152000   239  119   5  e
    5005  37182.156500   239  119   6  e
    ...
    6379  87147.136100   303  151  36  e
    6380  87937.894700   303  151  37  e
    6381  88698.357100   303  151  38  e
    6382  89427.550400   303  151  39  e
    6383  90124.333200   303  151  40  e
    ...
    [1383 rows x 5 columns]

As stated above, the ``states_chunks`` function actually returns generator:

.. code-block:: pycon

    >>> type(states_chunks)
    <class 'function'>

    >>> type(states_chunks(states_path, columns))
    <class 'generator'>

The indices of the data frames returned by the generator are of ``int`` data-type,
but *all the data columns* are of the data-type ``str`` (or more precisely
``dtype=object``, on the dataframe level). This needs to be kept in mind when accessing
data.

.. code-block:: pycon

    >>> chunks = list(states_chunks(states_path, columns))

    >>> chunk = chunks[0]

    >>> chunk.index.dtype
    dtype('int64')

    >>> chunk.dtypes
    E        object
    g_tot    object
    J        object
    v        object
    kp       object
    dtype: object

    >>> chunk.loc[3, "E"]
    '4260.062200'

    >>> type(chunk.loc[3, "E"])
    <class 'str'>

This approach was chosen to control the inconsistencies arising from letting ``pandas``
guess the correct data types, or having to supply the types manually. It is way easier
and more general to apply the correct type conversion downstream from this generator.


Examples of the ``trans_chunks`` usage:
=======================================

The ``trans_chunks`` function follows pretty much the same API as the ``states_chunks``,
with a couple of differences:

- The ``trans_chunks`` function does not need to know the columns labels. The columns
  are labeled automatically according the data format standard defined in the ExoMol
  release paper.

- The ``trans_paths`` argument to the function now accepts a *sequence* of paths, rather
  than a single path, as many datasets have more than a single trans file. The full
  sequence of paths to the files is passed to the function and the returned generator
  aggregates chunks of transitions data from all the trans files passed.

- The data types of the data-frames yielded by the generator (returned by
  ``trans_chunks``) are now *correct*, as in the first two columns are integer state
  indices, while the remaining column(s) is/are of the ``float`` type

- The indices of the yielded data frames are auto-generated and not representing
  anything other than simple counting index of the rows in the original files.

.. code-block:: pycon

    >>> from exomole.read_data import trans_chunks

    >>> trans_paths_list = list(str(path) for path in dataset_dir.glob("*.trans.bz2"))

    >>> # in this case, only as single .trans file exists for this dataset
    >>> trans_paths_list
    ['tests/resources/exomol_data/CO/12C-16O/Li2015/12C-16O__Li2015.trans.bz2']

    >>> for chunk in trans_chunks(trans_paths_list, chunk_size=1000):
    ...     print(chunk)
    ...     break  # break after first iteration, to limit the testing time of this code
            i     f          A_if       v_if
    0      84    42  1.155000e-06   2.405586
    1      83    41  1.161000e-06   2.441775
    2      82    40  1.162000e-06   2.477774
    3      81    39  1.159000e-06   2.513606
    4      80    38  1.152000e-06   2.549292
    ...
    995  1076  1034  1.854000e-02  73.892163
    996   845   803  4.062000e-07  73.905174
    997   892   850  1.044000e-03  73.905547
    998  1166  1124  3.007000e-02  74.057017
    999  1121  1079  2.416000e-02  74.085730
    ...
    [1000 rows x 4 columns]

    >>> chunk.dtypes
    i         int64
    f         int64
    A_if    float64
    v_if    float64
    ...