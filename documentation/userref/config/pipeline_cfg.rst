.. _pipeline_cfg:

++++++++++++++++++++++++++
Project Configuration File
++++++++++++++++++++++++++

The project configuration file provides a common configuration to all pipeline
runs which are part of a particular :ref:`project <config-overview>`. Through
this file, it is possible to configure the database used for pipeline runs,
the location in which jobs are stored, and the amount and storage location for
logging.

The default ``pipeline.cfg`` file is as follows:

.. literalinclude:: /../tkp/conf/project_template/pipeline.cfg

The file follows the :ref:`standard ConfigParser syntax <configparser>`.
Three special variables which may be used in expansions are provided provided
by the Trap: ``cwd``, the current working directory, ``start_time``, the time
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

``log_file``
   The full path to a file into which the pipeline will write logging
   information as it progresses. This file provides a record of pipeline
   activity, and, in particular, any errors or problems encountered. It is
   therefore important for reproducibility.

``debug``
   A boolean (True or False) value. If True, extra information will be written
   to the log file, which might be helpful in diagnosing hard-to-find
   problems.

``database`` Section
====================

``engine``
   The database engine to use. Two engines are supported: ``postgresql`` and
   ``monetdb``. See the :ref:`introductory material on databases
   <database-intro>` for details.

``host``, ``port``
   The host and port on the network at which the database server is listening.

``database``, ``user``, ``password``
   The name of the database to use, and the username and password required to
   connect to it.

``passphrase``
   A passphrase which provides administrative access to the database server.
   Only applicable to the ``monetdb`` engine. This is not required for normal
   operation, but enables the user to (for example) create and destroy
   databases.
