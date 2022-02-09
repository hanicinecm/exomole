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
nested data structures:

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

Apart from the data parsed from the unstructured *.def* file, several higher-level
methods are available for convenience:

.. code-block:: pycon

    >>> def_parser.get_quanta_labels()
    ['par', 'v', 'N', 'e/f']

    >>> # header expected for the .states file
    >>> def_parser.get_states_header()
    ['i', 'E', 'g_tot', 'J', 'tau', 'par', 'v', 'N', 'e/f']

Finally, a high-level function is provided for a quick and convenient parsing and
validation of dataset .def files identified by isotopologue slugs:

.. code-block:: pycon

    >>> from exomole.read_def import parse_def
    >>> # the data_dir_path argument is optional if called from within the exomol data directory
    >>> def_data = parse_def("40Ca-1H", data_dir_path=exomol_data_dir)
    >>> def_data
    <exomole.read_def.DefParser...>

    >>> def_data.get_quanta_labels()
    ['par', 'v', 'N', 'e/f']

    >>> # TODO: Finish the doc with errors etc...


.. _release paper: https://doi.org/10.1016/j.jms.2016.05.002