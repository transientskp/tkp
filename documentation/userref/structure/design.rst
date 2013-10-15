.. _design:

++++++
Design
++++++

As images flow through the Trap, they are processed by a series of distinct
pipeline components, or "stages". Each stage consists of Python logic,
often interfacing with the pipeline database.

A complete description of the logical design of the Trap is beyond the scope
of this document. Instead, the reader is referred to an upcoming publication
by Swinbank et al (`draft version
<https://github.com/transientskp/trap-paper>`_ now available to project
members only). Here, we sketch only an outline of the various pipeline stages.

Pipeline topology and code re-use
=================================

An early design goal of the Trap was that the various stages should be easily
re-usable in different pipeline topologies. That is, rather than simply
relying on "the" Trap, users should be able to mix-and-match pipeline
components to pursue their own individual science goals. This mode of
operation is not well supported by the current Trap, but some effort is made
to ensure that stages can operate as independent entities

.. _stages:

Pipeline stages
===============

.. toctree::
   :maxdepth: 1

   stages/startup
   stages/dump
   stages/persistence
   stages/quality
