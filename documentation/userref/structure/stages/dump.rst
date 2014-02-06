.. _stage-dump:

=============
Database dump
=============

Before performing any processing, the pipeline can be configured to dump a
backup copy of the database. This will enable convenient recovery (and, if
necessary, forensics) in the results of a pipeline failure mid-way through
processing. The dump is made to the job directory in a file named according to
the pattern ``<database host>_<database name>_<current time>.dump``.

This functionality may be enabled / disabled via the
``dump_backup_copy`` boolean in the
:ref:`database section <pipeline_cfg_database>` of the
:ref:`pipeline.cfg file <pipeline_cfg>`.