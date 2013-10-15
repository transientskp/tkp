.. _introduction:

++++++++++++
Introduction
++++++++++++

The LOFAR Transients Pipeline ("Trap") provides a means of searching a stream
of N-dimensional (two spatial, frequency, polarization) image "cubes" for
transient astronomical sources. The pipeline is developed specifically to
address data produced by the `LOFAR Transients Key Science Project
<http://www.transientskp.org>`_, but may also be applicable to other
instruments or use cases.

The Trap codebase provides the pipeline definition itself, as well as a number
of supporting routines for source finding, measurement, characterization, and
so on. Some of these routines are also available as :ref:`stand-alone tools
<tools>`.

.. _overview:

High-level overview
===================

The Trap consists of a tightly-coupled combination of a "pipeline definition"
-- effectively a Python script that marshals the flow of data through the
system -- with a library of analysis routines written in Python and a
database, which not only contains results but also performs a key role in data
processing.

Broadly speaking, as images are ingested by the Trap, a Python-based
source-finding routine scans them, identifying and measuring all point-like
sources. Those sources are ingested by the database, which :ref:`associates
<database-assoc>` them with previous measurements (both from earlier images
processed by the Trap and from other catalogues) to form a lightcurve.
Measurements are then performed at the locations of sources which were
expected to be seen in this image but which were *not* detected. A series of
statistical analyses are performed on the lightcurves constructed in this way,
enabling the quick and easy identification of potential transients. This
process results in two key data products: an *archival database* containing
the lightcurves of all point-sources included in the dataset being processed,
and *community alerts* of all transients which have been identified.

Some aspects of the data processing performed by the Trap are
compute-intensive. For this reason, it is possible to distribute processing
over a cluster. We use the :ref:`Celery <celery-intro>` distributed task queue for
this purpose.

Exploiting the results of the Trap involves understanding and analysing the
resulting lightcurve database. The Trap itself provides no tools directly
aimed at this. Instead, the Transients Key Science Project has developed the
`Banana <https://github.com/transientskp/banana>`_ web interface to the
database, which is maintained separately from the Trap. The database may also
be interrogated by end-user developed tools using `SQL
<https://en.wikipedia.org/wiki/SQL>`_.

Documentation layout
====================

The documentation is split into four broad sections:

:ref:`Getting Started <getstart>`
  Provides a guide to installing the Trap and its supporting libraries on
  common platforms and some basic information to help get up and running
  quickly.

:ref:`User's Reference <userref>`
  Here we provide a complete description of all the functionality available in
  the Trap and describe the various configuration and setup options available
  to the end user.

:ref:`Developer's Reference <devref>`
  A guide to the structure of the codebase, the development methodologies, and
  the functionality available in the supporting libraries. This is of interest
  both to developers within the project and to those who want to build upon
  Trap functionality for their own purposes.

:ref:`Stand-alone Tools <tools>`
  Some functionality developed for the Trap is also available in these simple,
  end-user focused tools.
