.. _scripts:

Scripts
*******

.. _tkp-manage:

tkp-manage.py
==============

the ``tkp-manage.py`` script is designed to be the new method for using the
TraP pipeline. It can setup a local pipeline working environment filled with
templates, create new jobs in this environment, start a job, clean a job and
probably more actions will be added in the future.

When the TraP is correctly installed on the system you can issue the
``tkp-manage.py`` command. Documentation of subcommands is also available
on the command line. You can use the ``--help`` flag (also per subcommand) to
explore all possible options.

.. program-output:: python ../tkp/bin/tkp-manage.py -h


initproject
-----------
Initialise a pipeline environment. As an end user this is the first thing you
want to do. It will set up a local environment which you can use to configure
your pipeline and for creating jobs. A project can be seen as a set of
configured jobs. When a project is initialised it is populated with a generic
setup that hopefully works for your setup, but probably the modification of
some of the configuration files is required.

A new project contains a ``manage.py`` script, which has the same functionality
as the ``tkp-manage.py``. People familiar with the Django framework will
recognize this.

.. program-output:: python ../tkp/bin/tkp-manage.py  initproject -h

initjob
-------
This command will initaliase a new job. It will setup a subfolder which is
populated with a set of templates you need to modify.

.. program-output:: python ../tkp/bin/tkp-manage.py initjob -h

run
---
Run will start a job. It needs a job name as argument.

.. program-output:: python ../tkp/bin/tkp-manage.py run -h

initdb
------

Initialise a database with the TKP schema. The semantics of this command vary
depending on the database system in use; see the :ref:`relevant section
<database-section>` for details.

.. program-output:: python ../tkp/bin/tkp-manage.py initdb -h


celery
------

Shortcut access to celery subcommands.

.. program-output:: python ../tkp/bin/tkp-manage.py celery -h
