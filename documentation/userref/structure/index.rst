.. _trap-design:

+++++++++++++++
Pipeline Design
+++++++++++++++

This section presents an overview of the fundamental algorithms used by, and
data flow through, the TraP. It is designed such that everyday users have a
full understanding of how their data is being processed. For implementation
details, please refer to the :ref:`devref`.

As images flow through the TraP, they are processed by a series of distinct
pipeline components, or "stages". Each stage consists of Python logic,
often interfacing with the pipeline database.

A complete description of the logical design of the TraP is beyond the scope
of this document. Instead, the reader is referred to an upcoming publication
by :ref:`Swinbank et al <swinbank-2014>`. Here, we sketch only an outline of
the various pipeline stages.

Pipeline topology and code re-use
=================================

An early design goal of the TraP was that the various stages should be easily
re-usable in different pipeline topologies. That is, rather than simply
relying on "the" TraP, users should be able to mix-and-match pipeline
components to pursue their own individual science goals. This mode of
operation is not well supported by the current TraP, but some effort is made
to ensure that stages can operate as independent entities

Image ordering and reproducibility
==================================

The material below describes each of the stages an image goes through as it is
processed through the pipeline. It is important to realise, though, that the
order in which images are processed is important due to the way in which
lightcurves are generated within the database: see the material on
:ref:`stage-association` for details. Reproducibility of pipeline results is
of paramount importance: the TraP guarantees that results will be reproducible
provided that images are always processed *in order of time*. That is, an
image from time :math:`t_n` must always be processed before an image from time
:math:`t_{n+1}`. In order to satisfy this condition, the TraP will internally
re-order images provided to it in the :ref:`images_to_process.py file
<config-job>` so that they are in time order. *If multiple TraP runs are to be
combined in a single dataset, the user must ensure that the runs are in an
appropriate sequence.*

It is worth noting the ordering of images across *frequency* is not important.

.. _stages:

Pipeline stages
===============

.. toctree::
   :maxdepth: 1

   stages/startup
   stages/dump
   stages/persistence
   stages/quality
   stages/extraction
   stages/association
   stages/nulldet
   stages/transient
