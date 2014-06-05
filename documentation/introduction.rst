.. _introduction:

++++++++++++
Introduction
++++++++++++

The LOFAR Transients Pipeline ("TraP") provides a means of searching a stream
of N-dimensional (two spatial, frequency, polarization) image "cubes" for
transient astronomical sources. The pipeline is developed specifically to
address data produced by the `LOFAR Transients Key Science Project
<http://www.transientskp.org>`_, but may also be applicable to other
instruments or use cases.

The TraP codebase provides the pipeline definition itself, as well as a number
of supporting routines for source finding, measurement, characterization, and
so on. Some of these routines are also available as :ref:`stand-alone tools
<tools>`.

.. _overview:

High-level overview
===================

The TraP consists of a tightly-coupled combination of a "pipeline definition"
-- effectively a Python script that marshals the flow of data through the
system -- with a library of analysis routines written in Python and a
database, which not only contains results but also performs a key role in data
processing.

Broadly speaking, as images are ingested by the TraP, a Python-based
source-finding routine scans them, identifying and measuring all point-like
sources. Those sources are ingested by the database, which :ref:`associates
<database-assoc>` them with previous measurements (both from earlier images
processed by the TraP and from other catalogues) to form a lightcurve.
Measurements are then performed at the locations of sources which were
expected to be seen in this image but which were *not* detected. A series of
statistical analyses are performed on the lightcurves constructed in this way,
enabling the quick and easy identification of potential transients. This
process results in two key data products: an *archival database* containing
the lightcurves of all point-sources included in the dataset being processed,
and *community alerts* of all transients which have been identified.

Exploiting the results of the TraP involves understanding and analysing the
resulting lightcurve database. The TraP itself provides no tools directly
aimed at this. Instead, the Transients Key Science Project has developed the
`Banana <https://github.com/transientskp/banana>`_ web interface to the
database, which is maintained separately from the TraP. The database may also
be interrogated by end-user developed tools using `SQL
<https://en.wikipedia.org/wiki/SQL>`_.

Documentation layout
====================

The documentation is split into four broad sections:

:ref:`Getting Started <getstart>`
  Provides a guide to installing the TraP and its supporting libraries on
  common platforms and some basic information to help get up and running
  quickly.

:ref:`User's Reference <userref>`
  Here we provide a complete description of all the functionality available in
  the TraP and describe the various configuration and setup options available
  to the end user.

:ref:`Developer's Reference <devref>`
  A guide to the structure of the codebase, the development methodologies, and
  the functionality available in the supporting libraries. This is of interest
  both to developers within the project and to those who want to build upon
  TraP functionality for their own purposes.

:ref:`Stand-alone Tools <tools>`
  Some functionality developed for the TraP is also available in these simple,
  end-user focused tools.

This documentation focuses on the technical aspects of using the TraP: all the
pipeline components are described, together with their user-configurable
parameters and the systems which have been developed for connecting them
together to form a pipeline. However, it does not provide detailed rationale
for all of the scientific choices made in the pipeline design. It is the
position of the author that achieving high quality results requires
understanding *both* the technical and the scientific choices made. For help
with the latter, the reader is referred to :ref:`Swinbank et al
<swinbank-2014>`>
