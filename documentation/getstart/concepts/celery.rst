.. _celery-intro:

++++++++++++++++++++++++++++
Task distribution via Celery
++++++++++++++++++++++++++++

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
this point (for example, if a bug is fixed in the Trap installation), the
worker *will continuing executing the old version of the code* until it is
stopped and restarted. If, for example, you are using a "daily build" of the
Trap code, you will need to restart your workers after each build to ensure
they stay up-to-date.

Finally, always bear in mind that it is possible to disable the whole task
distribution system and run the pipeline in a single process. This is simpler
to set up, and likely simpler to debug in the event of problems. But keep in
mind that a running broker is still required. To enable this mode, simple edit
your ``celeryconfig.py`` file and ensure it contains the (uncommented) line::

  CELERY_ALWAYS_EAGER = CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
