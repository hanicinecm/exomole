Parsing and validation of the exomol.all master file
****************************************************

The ``exomole.read_all.AllParser`` is a class dedicated to reading and parsing the
ExoMol master file *exomol.all*.
It may be called either from outside the ExoMol server, requesting the file over the
public API:

.. code-block:: pycon

    >>> from exomole.read_all import AllParser

    >>> all_parser = AllParser()

or from the ExoMol server, supplying the full path to the master file:

.. code-block:: pycon

    >>> from pathlib import Path

    >>> # replace with the relevant path on the server:
    >>> exomol_data_path = Path("tests/resources/exomol_data")
    >>> all_parser = AllParser(path=exomol_data_path/"exomol.all")

    >>> print(all_parser.raw_text[:300] + "...")
    EXOMOL.master                                                                   # ID
    20210707                                                                        # Version number with format YYYYMMDD
      80                                                                            # Number of molec...


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

Finally, a high-level function is provided, returning a parsed ``AllParser``, which
needs to be called either without arguments from within the exomol directory on the
server, or with a path leading to the data directory as a single argument:

.. code-block:: pycon

    >>> from exomole.read_all import parse

    >>> # again, swap the path for the real one on the server
    >>> parse(data_dir_path="tests/resources/exomol_data")
    <AllParser: parsed>

If the *exomol.all* file cannot be parsed for some reason (most likely because of the
structure of the file does not agree with the defined standard), the ``AllParseError``
is raised, hopefully detailing the reason.
The ``AllParser`` can also be instantiated with the ``warn_on_comments=True`` flag,

.. code-block:: pycon

    >>> all_parser = AllParser(warn_on_comments=True)

in which case the ``parse`` method will trigger warnings whenever some minor problems
are detected in the file, such as inconsistent comments, blank lines, etc.


.. _release paper: https://doi.org/10.1016/j.jms.2016.05.002