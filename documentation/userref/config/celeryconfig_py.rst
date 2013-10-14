.. _celeryconfig_py:

++++++++++++++++++++++++++
Celery Configuration File
++++++++++++++++++++++++++

The :ref:`management script <tkp-manage>` may be used to start a :ref:`Celery
<celery-intro>` worker. The worker is configured using the file
``celeryconfig.py`` in the :ref:`project directory <config-overview>`. The
default contents of this file are:

.. literalinclude:: /../tkp/conf/project_template/celeryconfig.py

Note that this file is Python code, and will be parsed as such. In fact, it is
a fully-fledged Celery configuration file, and the reader is referred to the
`main Celery documentation
<http://docs.celeryproject.org/en/latest/configuration.html>`_ for a complete
reference. Here, we highlight just the important parameters defined in the
defualt configuration.

Note the line::

  #CELERY_ALWAYS_EAGER = CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

By uncommenting this line (removing the initial ``#``), the pipeline is forced
to run in serial mode. That is, tasks are executed sequentially by a single
Python process. No broker and no workers are required. This will likely have a
significant impact on performance, but makes the system simpler and easier to
debug in the event of problems.

The line::

  BROKER_URL = CELERY_RESULT_BACKEND = 'amqp://guest@localhost//'

specifies the URL of the Celery broker, which is also the location to which
workers will return their results. Various different types of broker are
available (see our :ref:`introduction to Celery <celery-intro>` for
suggestions), and they must be configured and started independently of the
pipeline: the appropriate URL to use will therefore depend on the
configuration chosen for your local system.

The other parameters in the file -- ``CELERY_IMPORTS`` and
``CELERYD_HIJACK_ROOT_LOGGER`` -- should be left set to their default values.
