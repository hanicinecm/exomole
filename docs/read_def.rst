*************************************
Parsing and validating the .def files
*************************************

The ``exomole.read_def.DefParser`` is a class dedicated to reading and parsing the
ExoMol *.def* files belonging to different datasets.
The following text lists some of the useful examples, for greater detail, refer to the
code and docstrings.

The ``DefParser`` may be instantiated either from outside the ExoMol server, requesting
the file over the public API (in which case the ``molecule_slug``, ``isotopologue_slug``
and ``dataset_name`` arguments must be passed):

.. code-block:: pycon

    >>> from exomole.read_def import DefParser

    >>> def_parser = DefParser(
    ...     molecule_slug="ScH", isotopologue_slug="45Sc-1H", dataset_name="LYT"
    ... )

Alternatively, from within the ExoMol server, the ``DefParser`` can be instantiated
passing the path pointing to the relevant *.def* file, such as:

.. code-block:: pycon

    >>> from pathlib import Path
    >>> # replace the following with the real data directory path:
    >>> exomol_data_dir = Path("tests/resources/exomol_data")
    >>> def_file_path = exomol_data_dir.joinpath("CaH", "40Ca-1H", "Yadin", "40Ca-1H__Yadin.def")

    >>> def_parser = DefParser(path=def_file_path)

As with the ``AllParser`` (`docs <read_all.rst>`_), the raw text can be accessed even
before it gets parsed:

.. code-block:: pycon

    >>> print(def_parser.raw_text)
    EXOMOL.def  # ID
    (40Ca)(1H)  # IsoFormula
    40Ca-1H  # Iso-slug
    Yadin  # Isotopologue dataset name
    20160726  # Version number with format YYYYMMDD
    ...
    0.500  # Default value of temperature exponent for all lines

The ``DefParser`` can parse all the *.def* file data, if they adhere to the file
standard defined in the `release paper`_, and it stores the parsed data in convenient
nested data structures. This is done by calling the ``parse`` method:

.. code-block:: pycon

    >>> def_parser.parse()
    >>> def_parser.id
    'EXOMOL.def'

    >>> def_parser.iso_formula
    '(40Ca)(1H)'

    >>> def_parser.iso_slug
    '40Ca-1H'

    >>> def_parser.dataset_name
    'Yadin'

    >>> def_parser.version
    20160726

    >>> def_parser.mass
    40.970416

    >>> def_parser.isotopes
    [Isotope(40Ca), Isotope(1H)]

    >>> def_parser.lifetime_availability, def_parser.lande_factor_availability
    (True, False)

    >>> def_parser.num_states, def_parser.num_transitions
    (1892, 26980)

    >>> def_parser.quanta
    [Quantum(par), Quantum(v), Quantum(N), Quantum(e/f)]

    >>> def_parser.quanta[1].description, def_parser.quanta[1].label
    ('State vibrational quantum number', 'v')

If the .def file cannot be parsed by ``parse`` for some reason (most likely because of
the structure of the file does not agree with the defined standard), the
``DefParseError`` is raised, hopefully detailing the reason.

The ``AllParser.parse`` method will also trigger warnings, whenever any minor problems
are detected in the file, such as inconsistent comments, blank lines, etc.
To suppress these warnings, the ``parse`` method can be called with the optional
``warn_on_comments=False`` argument:

.. code-block:: pycon

    >>> def_parser.parse(warn_on_comments=False)

Apart from the data parsed from the unstructured *.def* file, several higher-level
methods are available for convenience:

.. code-block:: pycon

    >>> def_parser.get_quanta_labels()
    ['par', 'v', 'N', 'e/f']

    >>> # header expected for the .states file
    >>> def_parser.get_states_header()
    ['i', 'E', 'g_tot', 'J', 'tau', 'par', 'v', 'N', 'e/f']

The ``check_consistency`` method goes a step further beyond just parsing, and checks
if the *.states* file and at least one *.trans* file exist, and if the .states has
the number of columns consistent with ``DefParser.get_states_header()``.
It will raise ``DefConsistencyError`` if any of the checks fail:

.. code-block:: pycon

    >>> def_parser.check_consistency()
    Traceback (most recent call last):
     ...
    exomole.exceptions.DefConsistencyError: A '40Ca-1H__Yadin.states(.bz2)' file needs to exist in tests/resources/exomol_data/CaH/40Ca-1H/Yadin!

Finally, a high-level function is provided for a quick and convenient parsing and
validation of the dataset .def files identified by isotopologue slugs. This is only
available if called on the ExoMol server.

.. code-block:: pycon

    >>> from exomole.read_def import parse_def
    >>> # the data_dir_path argument is optional if called from within the exomol data directory
    >>> def_data = parse_def("40Ca-1H", data_dir_path=exomol_data_dir)
    >>> def_data
    <exomole.read_def.DefParser...>

    >>> def_data.get_quanta_labels()
    ['par', 'v', 'N', 'e/f']

If there is more than a single dataset available for the given isotopologue, an
exception is raised and the ``dataset_name`` attribute needs to be passed to the
``parse_def`` function also.

.. code-block:: pycon

    >>> def_data = parse_def("24Mg-1H", data_dir_path=exomol_data_dir)
    Traceback (most recent call last):
      ...
    exomole.exceptions.DefParseError: Multiple .def files found:
      tests/resources/exomol_data/MgH/24Mg-1H/MoLLIST/24Mg-1H__MoLLIST.def
      tests/resources/exomol_data/MgH/24Mg-1H/Yadin/24Mg-1H__Yadin.def
    Please pass the dataset_name argument.


.. _release paper: https://doi.org/10.1016/j.jms.2016.05.002