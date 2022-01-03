
***********************
Introduction to ExoMole
***********************

Meet **ExoMole**, a creature that feeds on data and meta-data files of the
ExoMol_ database.
ExoMole package provides code for parsing, validation and access to the ExoMol
meta-data and data either from local file system or over the ExoMol public API defined
in the database `release paper`_.

The code in the package is organised into several modules. The ``read_all`` and
``read_def`` modules contain functionality for parsing, validation and analysis of the
ExoMole's *.all* and *.def* meta-data files, while the ``read_data`` module groups
functionality for reading and validating the *.states* and *.trans* data files.


Installation:
=============

The ``exomole`` package can be installed either from PyPI_

.. code-block:: bash

    python3 -m pip install exomole

or from the GitHub_ page

.. code-block:: bash

    python3 -m pip install git+https://github.com/hanicinecm/exomole.git

or from the source by navigating to the project root directory and running

.. code-block:: bash

    python3 -m pip install .


For Developers:
===============
It goes without saying that any development should be done in a clean virtual
environment.
After cloning or forking the project from its GitHub_ page, ``exomole`` can be
installed into the virtual environment in the editable mode by running

.. code-block:: bash

    pip install -e .[dev]

The ``[dev]`` extra installs (apart from the package dependencies) also several
development-related packages, such as ``pytest``, ``black``, ``tox`` or ``ipython.``
The tests can then be executed by running (from the project root directory)

.. code-block:: bash

    pytest --cov --doctest-modules

The project does not have the ``requirements.txt`` file by design, as all the package
dependencies are rather handled by the ``setup.py``.
The package therefore needs to be installed locally to run the tests, which grants the
testing process another layer of usefulness.

Docstrings in the project adhere to the numpydoc_ styling.
The project code is formatted by ``black``.
Always make sure to format your code before submitting a pull request, by running
``black`` on all your python files.


.. _ExoMol: https://www.exomol.com/
.. _release paper: https://doi.org/10.1016/j.jms.2016.05.002
.. _GitHub: https://github.com/hanicinecm/exomole
.. _PyPI: https://pypi.org/project/exomole/
.. _numpydoc: https://numpydoc.readthedocs.io/en/latest/format.html