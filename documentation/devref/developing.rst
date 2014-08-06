.. _developing:

+++++++++++++++++++++++++
Guidelines for Developers
+++++++++++++++++++++++++

This documents deals (shortly) with writing software for the
Transients Pipeline, either the TraP part (recipes) or the underlying
modules (the TKP package).

Coding guidelines
=================

We try to follow PEP 8 as much as possible, although at times, this is
flexible (e.g., short variable names sometimes make more sense in the
context; and there is no hard rule where braces or parentheses should
go when they cover more than one line).

Occasionally, it may be useful to run pylint (or similar) on the code,
to pick out a few things (unused variables and such). Don't aim to get
a 10/10 score, just use the suggestions by pylint where deemed
applicable.



Documentation
=============

All documentation in the `code` part of the TKP repository is written
in restructured text, whether doc strings or longer documents, and is
then put together and transformed using Sphinx. By 'put together', we
mean that Sphinx will pick up the doc strings from referenced modules
and add this to the other documentation; by transformed we mean the
Sphinx will create HTML pages out of the documentation. The latter is
done on a nightly basis, so that documentation is refreshed over
night.

There currently exists two main sections of documentation:

- TraP: this section deals with setting up and running the transients
  pipeline, as well as more details about the individual recipes.

- TKP: this section deals with the underlying modules and algorithms
  used in the transients pipeline.

Using the intersphinx extension, links can be and are created between
the two documentation sections.

Doc strings
-----------

For doc strings we use the `sphinxcontrib-napoleon
<https://pypi.python.org/pypi/sphinxcontrib-napoleon>`_ syntax, since
it is much more clear to read than the suggested PEP 8 syntax or
default Sphinx Syntax. Example::

    Args:
        path (str): The path of the file to wrap
        field_storage (FileStorage): The :class:`FileStorage` instance to wrap
        temporary (bool): Whether or not to delete the file when the File
           instance is destructed

    Returns:
        BufferedFileStorage: A buffered writable file descriptor


Testing
=======

No (good) piece of software can be without proper tests. In the case
of the TKP library, a (presumably) most tests have come after the fact
(i.e., first the problem was solved, then it was tested if that really
worked properly), and often tests were initially practical use cases,
and not so much stylized unit tests.

As a result, there are probably still many routines that lack proper
unit tests, although more unit tests are still being added.

I suggest to follow at least one simple rule:

.. pull-quote::

   **If a bug shows up and is fixed, or a function is changed, write a
   unit test, detailing the bug (and its fix) or the change.**


Unit tests
----------

The unit tests use the Python 2.7's :mod:`unittest` module.

Running the unit tests
----------------------

To run the unit tests, there exists a test subdirectory outside of the
TKP package (at :file:`tkp/trunk/tests`). The :file:`runtests.bash`
script sets up the necessary paths and allows to call the various unit
tests as an argument to the script. In the end, this was done to
`ctest` can automatically run each unit test as a separate test (the
various path settings inside the script are optimized for in-build
testing with cmake and ctest).

To run all the tests at once, one can also use the :file:`test.py`
script, provided all the paths are set correctly.


Pipeline tests
--------------

Ultimately, the only way to know if everything works correctly (or as
correct as can be deduced), is by running the transients
pipeline. Work is still in progress to set up a set of simulated data
that will test the various aspects of the pipeline, including proper
source finding, association and classification, even under rare (bad),
but controlled (simulated) circumstances.

For now, I would suggest to have a look at
:file:`/home/evert/work/trap/jobs/bell/control/runtrap.sh`, and work
back from this file for the necessary setup. I have been using this
(small) dataset to at least test the basic functionality of the
transients pipeline. Practically, running these data through the
pipeline should produce about five transients (although none of them
are real: they are just artefacts of, liekely, flux calibration
problems).
