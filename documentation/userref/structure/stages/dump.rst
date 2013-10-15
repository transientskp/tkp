.. _stage-dump:

=============
Database dump
=============

Before performing any processing, the pipeline can be configured to dump a
backup copy of the database. This will enable convenient recovery (and, if
necessary, forensics) in the results of a pipeline failure mid-way through
processing. The dump is made to the job directory in a file named according to
the pattern ``<database host>_<database name>_<current time>.dump``.

The following parameters may be configured in the :ref:`job configuration file
<job_params_cfg>`:

Section ``db_dump``
-------------------

``db_dump``
   Boolean. ``True`` to enable the database dump, ``False`` to disable.
