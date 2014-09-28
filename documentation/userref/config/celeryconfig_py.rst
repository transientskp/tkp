

.. _celery-intro:


++++++++++++++++++++++++++++
Task distribution via Celery
++++++++++++++++++++++++++++

.. Warning::

    TRAP runs in parallel by default now, no extra action like running celery
    workers is required. You should only try to use celery if you want to
    distribute work over multiple machines.


`Celery <http://celeryproject.org/>`_ provides a mechanism for distributing
tasks over a cluster of compute machines by means of an "asynchronous task
queue". This means that users submit jobs to a centralised queueing system (a
"broker"), and then one or more worker processes collect and process each job
from the queue sequentially, returning the results to the original submitter.

Celery is a flexible but complex system, and the details of its configuration
fall outside the scope of this document. The user is, instead, referred to the
`Celery documentation <http://celeryproject.org/docs-and-support/>`_. Here,
we provide only some brief explanation.

If you would like to take advantage of the task distribution system, you will
need to set up a broker and one or more workers which will process tasks from
it. There are a number of `different brokers available
<http://docs.celeryproject.org/en/latest/getting-started/brokers/>`_, each
with their own pros and cons: `RabbitMQ <http://www.rabbitmq.com/>`_ is a fine
default choice.

Workers can be started by using the ``celery worker`` option to the
:ref:`tkp-manage.py <tkp-manage>` script. Indeed, ``tkp-manage.py`` provides a
convenient way of interfacing with a variety of Celery subcommands: try
``tkp-manage.py celery -h`` for information.

When you start a worker, you will need to configure it to connect to an
appropriate broker. If you are using the ``tkp-manage.py`` script, you can
configure the worker through the file :ref:`celeryconfig.py <celeryconfig_py>`
in your :ref:`project folder <config-overview>`: set the ``BROKER_URL``
variable appropriately. Note that if you are running the broker and a worker
on the same host with a standard configuration, the default value should be
fine.

Note that a single broker and set of workers can be used by multiple different
pipeline users. If running on a shared system, it is likely sensible to
regard the broker and workers as a "system service" that all users can access,
rather than having each user try to run their own Celery system.

Note also that a worker loads all the necessary code to perform its
tasks into memory when it is initalized. If the code on disk changes after
this point (for example, if a bug is fixed in the TraP installation), the
worker *will continuing executing the old version of the code* until it is
stopped and restarted. If, for example, you are using a "daily build" of the
TraP code, you will need to restart your workers after each build to ensure
they stay up-to-date.

Finally, always bear in mind that it is possible to disable the whole task
distribution system and run the pipeline in a single process. This is simpler
to set up, and likely simpler to debug in the event of problems. But keep in
mind that a running broker is still required. To enable this mode, simple edit
your ``celeryconfig.py`` file and ensure it contains the (uncommented) line::

  CELERY_ALWAYS_EAGER = CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


Run Celery workers
==================

If you want to parallelize TraP operations using celery, you need to run a
separate Celery worker. This worker will receive jobs from a broker, so it is
assumed you installed and started a broker in the installation step. Start a
Celery worker by running::

    % tkp-manage.py celery worker

If you want to increase the log level add ``--loglevel=info`` or maybe even
``debug`` to the command. If you dont want to use a Celery worker (run the
pipeline is serial mode) uncomment this line in the ``celeryconfig.py`` file in
your pipline directory::

    #CELERY_ALWAYS_EAGER = CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

Note that a running broker is still required.


.. _celeryconfig_py:

Celery Configuration File
=========================

The :ref:`management script <tkp-manage>` may be used to start a :ref:`Celery
<celery-intro>` worker. The worker is configured using the file
``celeryconfig.py`` in the :ref:`project directory <config-overview>`. The
default contents of this file are:

.. literalinclude:: /../tkp/config/project_template/celeryconfig.py

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
