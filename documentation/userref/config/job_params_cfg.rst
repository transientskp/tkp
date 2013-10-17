.. _job_params_cfg:

++++++++++++++++++++++++++++
Job Parameters Configuration
++++++++++++++++++++++++++++

The job parameters file provides the detailed, scientifically-motivated
settings for each pipeline step. Providing the appropriate configuration here
is essential for achieving scientifically valid results.

The default ``job_params.cfg`` file is as follows:

.. literalinclude:: /../tkp/conf/job_template/job_params.cfg

The file follows the :ref:`standard ConfigParser syntax <configparser>`.

A detailed description of each of the parameters in this file is provided in
the documentation for the relevant :ref:`pipeline stage <stages>`.
