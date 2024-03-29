.. _pipeline_cfg:

+++++++++++++++++++++++++++++++++++++++++++++
``pipeline.cfg`` - Project Configuration File
+++++++++++++++++++++++++++++++++++++++++++++

The project configuration file provides a common configuration to all pipeline
runs which are part of a particular :ref:`project <config-overview>`. Through
this file, it is possible to configure the database used for pipeline runs,
the location in which jobs are stored, and the amount and storage location for
logging.

The default ``pipeline.cfg`` file is as follows:

.. literalinclude:: /../tkp/config/project_template/pipeline.cfg

The file follows the :ref:`standard ConfigParser syntax <configparser>`.
Three special variables which may be used in expansions are provided provided
by the TraP: ``cwd``, the current working directory, ``start_time``, the time
at which the current pipeline job is started and ``job_name``, the name of the
job currently being executed.

``DEFAULT`` section
===================

The ``DEFAULT`` section provides a location for defining parameters which may
be referred to be other sections. The following parameters may be defined:

``runtime_directory``
   This is the root directory for the project. The default value, ``%(cwd)s``,
   means that the pipeline.cfg refers to the project in the directory in which
   it is stored: this is almost always correct.

``job_directory``
   This is the directory under which new jobs will be created. The default is
   to create a directory named after the job as a subdirectory of the project
   directory. This is almost always correct.

``logging`` section
===================

``log_dir``
   The full path to a directory into which the pipeline will write logging
   information as it progresses, and also make a record of the parameters used
   for a job. The log file provides a record of pipeline
   activity, and, in particular, any errors or problems encountered, while the
   parameter files record the configuration that produced these results.
   This folder is therefore important for reproducibility and debugging
   purposes.

``debug``
   A boolean (True or False) value. If True, extra information will be written
   to the log file, which might be helpful in diagnosing hard-to-find
   problems.

.. _pipeline_cfg_database:

``database`` Section
====================

.. note::
   The database config settings can be over-ridden using environment
   variables, e.g. for configuring a unit-testing environment.
   See :py:func:`tkp.config.get_database_config` for details.

``engine``
   The database engine to use. One engine is supported:
   ``postgresql``.
   See the :ref:`introductory material on databases
   <database-intro>` for details.

``host``, ``port``
   The host and port on the network at which the database server is listening.

``database``, ``user``, ``password``
   The name of the database to use, and the username and password required to
   connect to it.

``dump_backup_copy``
   A boolean value. If True, a copy of the configured database will be
   dumped to disk at the beginning of each pipeline run. This is not
   recommended in regular use, but can be useful if encountering
   intermittent database errors, both for recovering a working database,
   and diagnosing how errors occur.
   The dump is made to the job directory in a file named according to
   the pattern ``<database host>_<database name>_<current time>.dump``.

.. _pipeline_cfg_image_cache:

``image_cache`` Section
=======================

This section configures the image caching functionality.


``copy_images``
   Boolean. If ``True``, image pixel data will be stored to a MongoDB database.


.. _pipeline_cfg_parallelise:

``parallelise`` Section
=======================

``method``
   Determines whether the TraP is run in single-process or multi-process mode.
   ``"multiproc"`` should be suitable for most users.

``cores``
   Determines the number of cores to use in multi-process mode. ``0`` will
   attempt to autodetect (and use all available cores).

