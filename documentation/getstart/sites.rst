.. _sites:

++++++++++++++++++++++++++
Site-specific setup guides
++++++++++++++++++++++++++

Amsterdam
=========

Set up your environment
-----------------------

If you have an account on the ``heastro1`` machine, all the software needed to
run the Trap has already been installed. You can add it to your environment by
running::

  $ . /opt/tkpenv/init.sh

(assuming you use ``bash`` as your shell: if not, all bets are off).

Get access to a database
------------------------

Regular users in Amsterdam do not have access to create their own database for
use with the Trap. Please speak to an administrator, and ask them to create
one for you. The database will be created on the machine
``heastrodb.science.uva.nl``, and will generally have the database name and
password set equal to your username. Discuss with the administrator whether
the database is using MonetDB or PostgreSQL.

Initialize a project directory
------------------------------

The :ref:`project directory <config-overview>` holds common settings for a
collection of pipeline runs.  Choose a location, and run::

  $ tkp-manage.py initproject <projectname>

Within your project directory, you will find a file ``pipeline.cfg``.
Customize it so that the ``[database]`` section matches the database created
above. It should look something like::

  [database]
  engine = monetdb
  database = <username>
  user = <username>
  password = <username>
  host = heastrodb
  port = 50000
  passphrase =

Check that all the fields match the values given to you by the administrator.
Generally, the ``passphrase`` entry will be blank.

If you wish, you can also customize the other fields in ``pipeline.cfg``: see
the :ref:`config-overview` section for details. Generally, the defaults are
fine.

Create and configure a job
--------------------------

Your pipeline project directory can contain multiple jobs. Jobs are a list of
files to process, and a set of "parset" (parameter set) files that can be used
to define various properties used during processing. To initialise a job, from
within your project directory run::

    $ ./manage.py initjob <jobname>

This will create a subdirectory in your pipeline directory. This directory
contains a a file names ``images_to_process.py``. This is a python script that
is used to generate a list of paths to images. You will need to adjust this to
point to your data files.

There is also a subdirectory named ``parsets`` which contains the parset files
described above.

Optionally, run Celery workers
------------------------------

.. Warning::

   What happens if there are other Celery workers already running on heastro1?

You may parallelize some pipeline operations by distributing them over a
number of Celery "worker" nodes. You can start one or more Celery workers by
running::

    % ./manage.py celery worker

Distributing jobs over multiple workers in this way might increase
performance, but can make debugging harder and problems more complex to
diagnose. You might therefore prefer not to run any workers, at least until
you have verified that everything works properly. In that case, edit
``celeryconfig.py`` in your pipeline directory and set::

    #CELERY_ALWAYS_EAGER = CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


Run the pipeline
----------------

To start crunching your data, run (from your pipeline directory)::

    $ ./manage.py run <jobname>

Note that you need to supply the database (see ``-h``) configuration if you
didn't add it it the ``pipeline.cfg`` file (or if you are not happy with the
defaults).
