*************************************************
Parsing and validating the exomol.all master file
*************************************************

The ``exomole.read_all.AllParser`` is a class dedicated to reading and parsing the
ExoMol master file *exomol.all*.
The following text lists some of the useful examples, for greater detail, refer to the
code and docstrings.

The ``AllParser`` may be instantiated either from outside the ExoMol server, which
requests the file over the public API:

.. code-block:: pycon

    >>> from exomole.read_all import AllParser

    >>> all_parser = AllParser()

or from the ExoMol server, in which case the full path to the master file needs to be
supplied:

.. code-block:: pycon

    >>> from pathlib import Path

    >>> # replace with the relevant path on the server:
    >>> exomol_data_path = Path("tests/resources/exomol_data")
    >>> all_parser = AllParser(path=exomol_data_path/"exomol.all")

    >>> print(all_parser.raw_text)
    EXOMOL.master                                                                   # ID
    20210707                                                                        # Version number with format YYYYMMDD
      80                                                                            # Number of molecules in the database
    ...
    20201201                                                                        # Version number with format YYYYMMDD

The ``AllParser`` can parse all the master file data, if they adhere to the file
standard defined in the `release paper`_, and it stores the parsed data in convenient
nested structures:

.. code-block:: pycon

    >>> all_parser.parse()
    >>> all_parser.id
    'EXOMOL.master'

    >>> all_parser.version
    20210707

    >>> len(all_parser.molecules)
    80

    >>> list(all_parser.molecules.keys())[:10]
    ['H2O', 'CO2', 'CO', 'CH4', 'NO', 'SO2', 'NH3', 'HNO3', 'OH', 'HF']

    >>> mol = all_parser.molecules["OH"]
    >>> mol
    Molecule(OH)

    >>> mol.isotopologues
    {'(16O)(1H)': Isotopologue(16O-1H)}

    >>> iso = mol.isotopologues["(16O)(1H)"]
    >>> iso.version
    20180719

    >>> iso.dataset_name
    'MoLLIST'

    >>> iso.inchi_key
    'TUJKJAMUKRIRHC-UHFFFAOYSA-N'

Finally, a high-level function is provided, returning a parsed ``AllParser`` instance.
The ``parse`` function needs to be called either without arguments from within the
exomol directory on the server, or with a path leading to the data directory as a
single argument:

.. code-block:: pycon

    >>> from exomole.read_all import parse_master

    >>> # again, swap the path for the real one on the server
    >>> parse_master(data_dir_path="tests/resources/exomol_data")
    <exomole.read_all.AllParser...>

If the *exomol.all* file cannot be parsed for some reason (most likely because of the
structure of the file does not agree with the defined standard), the ``AllParseError``
is raised, hopefully detailing the reason.
The ``AllParser.parse`` method will also trigger warnings, whenever any minor problems
are detected in the file, such as inconsistent comments, blank lines, etc.
To suppress these warnings, the ``parse`` method can be called with the optional
``warn_on_comments=False`` argument,

.. code-block:: pycon

    >>> all_parser = all_parser.parse(warn_on_comments=False)


.. _release paper: https://doi.org/10.1016/j.jms.2016.05.002