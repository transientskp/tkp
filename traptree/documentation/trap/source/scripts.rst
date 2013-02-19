.. _scripts-section:

#######
Scripts
#######

.. |last_updated| last_updated::

:Last updated: |last_updated|

This page gives a very brief description of scripts used in the
TraP workflow, and details the parameters supplied via command line
arguments .

trap-manage.py
==============

the ``trap-manage.py`` script is designed to be the new method for using the
TRAP pipeline. It can setup a local pipeline working environment filled with
templates, create new jobs in this environment, start a job, clean a job and
probably more actions will be added in the future.

When the TRAP is correctly installed on the system you can issue the
``trap-manage.py`` command. Documentation of subcommands is also available
on the command line. You can use the ``--help`` flag (also per subcommand) to
explore all possible options.

.. program-output:: python ../../trap/bin/trap-manage.py -h


initproject
-----------
Initialise a pipeline environment. As an end user this is the first thing you
want to do. It will set up a local environment which you can use to configure
your pipeline and for creating jobs. A project can be seen as a set of
configured jobs. When a project is initialised it is populated with a generic
setup that hopefully works for your setup, but probably the modification of
some of the configuration files is required.

A new project contains a ``manage.py`` script, which has the same functioality
as the ``trap-manage.py``. People familiar with the Django framework will
recognize this.

.. program-output:: python ../../trap/bin/trap-manage.py  initproject -h

initjob
-------
This command will initaliase a new job. It will setup a subfolder which is
populated with a set of templates you need to modify.

.. program-output:: python ../../trap/bin/trap-manage.py initjob -h

run
---
Run will start a job. It needs a job name as argument.

.. program-output:: python ../../trap/bin/trap-manage.py run -h

runlocal
--------

This command will run the pipeline in a non-distributed way. This is mainly
intended for development purposes but may speedup your pipeline if you use
it on a single machine.

.. program-output:: python ../../trap/bin/trap-manage.py run -h

clean
-----

Will cleanup a job.

.. program-output:: python ../../trap/bin/trap-manage.py clean -h


info
----

Will print some info/statistics about a job.

.. program-output:: python ../../trap/bin/trap-manage.py info -h
