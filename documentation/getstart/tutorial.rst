+++++++++++++++++
Tutorial Overview
+++++++++++++++++

This page walks you through setting up a complete, stand-alone Trap
environment running on your own system. See also our :ref:`site-specific
guides <sites>`.

Install the software
====================

First of all, the software should be installed on your system. See :ref:`the
installation manual <installation>`.

Create a pipeline project directory
===================================

Create a project directory which is a container of your pipeline settings and job
files. Run these command to initialise a project directory in your home
directory::

    $ cd ~
    $ tkp-manage.py initproject <projectname>

.. _getstart-initdb:

Initialize a database
=====================

The pipeline requires a database for storing data. To initialise a database
the trap manage ``initdb`` subcommand can be used (from the project directory)::

  $ ./manage.py initdb

Use the ``-h`` flag to see an explanation about how to set the various
properties.  If you don't want to set these properties all the time, you can
add a ``[database]`` section to your pipeline.cfg.


Run Celery workers
==================

If you want to parallelize trap operations, you need to run a separate Celery
worker. This worker will receive jobs from a broker, so it is assumed you
installed and started a broker in the installation step. Start a Celery worker
by running::

    % ./manage.py celery worker

If you want to increase the log level add ``--loglevel=info`` or maybe even
``debug`` to the command. If you dont want to use a Celery worker (run the
pipeline is serial mode) uncomment this line in the ``celeryconfig.py`` file in
your pipline directory::

    #CELERY_ALWAYS_EAGER = CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

Note that a running broker is still required.


Create and configure a job
==========================

Your pipeline project directory can contain multiple jobs. Jobs are a list of
files to process, and a set of "parset" (parameter set) files that can be used
to define various properties used during processing. To initialise a job run::

    $ ./manage.py initjob <jobname>

This will create a subdirectory in your pipeline directory. This directory
contains a a file names ``images_to_process.py``. This is a python script that
is used to generate a list of paths to images. You will need to adjust this to
point to your data files.

There is also a subdirectory named ``parsets`` which contains the parset files
described above.

Run the pipeline
================

To start crunshing your data run (from your pipeline directory)::

    $ ./manage.py run <jobname>

Note that you need to supply the database (see ``-h``) configuration if you
didn't add it it the ``pipeline.cfg`` file (or if you are not happy with the
defaults).
