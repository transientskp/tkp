.. _design:

++++++
Design
++++++

As images flow through the Trap, they are processed by a series of distinct
pipeline components, or "steps". Each step consists of Python logic,
often interfacing with the pipeline database.

A complete description of the logical design of the Trap is beyond the scope
of this document. Instead, the reader is referred to an upcoming publication
by Swinbank et al (`draft version
<https://github.com/transientskp/trap-paper>`_ now available to project
members only). Here, we sketch only an outline of the various pipeline steps.

Pipeline topology and code re-use
=================================

An early design goal of the Trap was that the various steps should be easily
re-usable in different pipeline topologies. That is, rather than simply
relying on "the" Trap, users should be able to mix-and-match pipeline
components to pursue their own individual science goals. This mode of
operation is not well supported by the current Trap, but some effort is made
to ensure that steps can operate as independent entities

Pipeline steps
==============

.. _step-config:

Configuration and startup
-------------------------

Before starting, the :ref:`project and job directories <config-overview>`
should be initialized appropriately, they key configuration files --
``pipeline.cfg``, ``celeryconfig.py``, ``images_to_process.py`` and
``job_params.cfg`` -- should be customized appropriately, and, if required, a
Celery broker and one or more workers shouldbe running. The pipeline is then
started by running::

   $ ./manage.py run <jobname>

from within the project directory.

.. _step-dump:

Database dump
-------------

Before performing any processing, the pipeline can be configured to dump a
backup copy of the database. This will enable convenient recovery (and, if
necessary, forensics) in the results of a pipeline failure mid-way through
processing. The dump is made to the job directory in a file named according to
the pattern ``<database host>_<database name>_<current time>.dump``.

The database dump may be enabled in ``job_params.cfg`` by setting::

   [db_dump]
   db_dump = True

or, similarly, setting ``db_dump = False`` to disable it.

.. _step-persistence:

Persistence
-----------

A record of all images to be processed is made in the database. Within the
database, images are sorted into :ref:`datasets <dataset>`, which group
related images together for processing: searches for transients are performed
between images in a single databset, for instance. All images being processed
are added to the same dataset.

Optionally, a copy of the image pixel data may be stored to a :ref:`MongoDB
<mongodb-intro>` instance at the same time.

The persistence step is configured via ``job_params.cfg``::

  [persistence]
  description = "TRAP dataset"
  dataset_id = -1
  copy_images = True
  mongo_port = 27017
  mongo_db = "tkp"
  ## for development:
  mongo_host = "localhost"
  ## for heastro1:
  #mongo_host = "pc-swinbank.science.uva.nl"
