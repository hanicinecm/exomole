***********************
Introduction to ExoMole
***********************

Meet **ExoMole**, a creature that feeds on data and meta-data files of the
ExoMol_ database.
The ``exomole`` package provides code for parsing, validation and access to the ExoMol
meta-data and data.
The package is primarily used for ExoMol database developers and maintainers, as most of
the features require access to the ExoMol files. The code therefore works the best if
installed directly on the ExoMol server.
Nevertheless, several features of the package are also relevant from outside the ExoMol
production server, tapping into the ExoMol public API defined in the database
`release paper`_.


.. image:: ./exomole.png
  :width: 450
  :align: center


Documentation:
==============

The code in the package is organised into several modules. The ``read_all`` and
``read_def`` modules contain functionality for parsing, validation and analysis of the
ExoMole's *.all* and *.def* meta-data files, while the ``read_data`` module groups
functionality for reading and validating the *.states* and *.trans* data files.

The links below provide some basic examples of usage of the code. For greater detail,
refer to the code and docstrings.

- ``read_all`` `examples <read_all.rst>`_
- ``read_def`` `examples <read_def.rst>`_
- ``read_data`` `examples <read_data.rst>`_


.. _ExoMol: https://www.exomol.com/
.. _release paper: https://doi.org/10.1016/j.jms.2016.05.002
