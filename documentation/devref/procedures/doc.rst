Documentation
=============

Requirements
------------

All parts of the TraP should be documented *both* at a level that is suitable
for end users using the pipeline and for developers who wish to understand,
fix and extend the codebase. Broadly, that distinction reflects the structure
of this manual. Note that we expect that developers will benefit both
automatically generated API documentation, making use of appropriate
docstrings in the code, and higher-level descriptions of system architecture
and functionality: both should be provided.

All new features or changes *must* be accompanied by appropriate
documentation. Reviewers are required to check that pull requests are well
documented before merging. See the material on :ref:`code-review` for details.

Technical details
-----------------

Documentation is written using `Sphinx`_. The documentation for the ``HEAD`` of
the ``master`` branch of the ``transientskp/tkp`` repository is, together with
the documentation for all released versions, is automatically build every night
and put online at http://docs.transientskp.org/.

Docstrings should make use of the "`Napoleon`_" syntax. For example::

  Args:
      path (str): The path of the file to wrap
      field_storage (FileStorage): The :class:`FileStorage` instance to wrap
      temporary (bool): Whether or not to delete the file when the File
         instance is destructed

  Returns:
      BufferedFileStorage: A buffered writable file descriptor

.. _Sphinx: http://www.sphinx-doc.org/
.. _Napoleon: https://pypi.python.org/pypi/sphinxcontrib-napoleon
