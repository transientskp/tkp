.. _getstart:

+++++++++++++++
Getting Started
+++++++++++++++

Install the software
====================

First of all, the software should be installed on your system. see the
installation manual. :ref:`installation`.

create a pipeline project folder
================================

Create a project folder which is a container of your pipeline settings and job
files. Run these command to initialise a project folder in homedir::

    $ cd ~
    $ tkp-manage.py initproject <projectname>


Initialize a database
=====================

The pipeline requires a database for storing data. To initialise a database
the trap manage `initdb` subcommand can be used (from the project folder)::

  $ ./manage.py initdb

Use the -h flag to see an explanation about how to set the various properties.
If you don't want to set these properties all the time, you can add a [database]
section to your pipeline.cfg.

Run celery workers
==================

If you want to parallelize trap operations, you need to run a separate celery
worker. This worker will receive jobs by a broker, so it is assumed you installed
and started a broker in the installation step. Start a celery worker by running::

    % ./manage.py celery worker

If you want to increase the log level add `--loglevel=info` or maybe even
`debug` to the command. If you dont want to use a celery worker (run the
pipeline is serial mode) uncomment this line in the `celeryconfig.py` file in
your pipline folder::

    #CELERY_ALWAYS_EAGER = CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


Create and configure a Job
==========================

Your pipeline project folder can contain multiple jobs. Jobs are a list of
files to process, and a set of `parset` (parameter set) files that can be used
to define various properties used during processing. To initialise a job run::

    $ ./manage.py initjob <jobname>

This will create a subfolder in your pipeline folder. This folder containts a
a file names `images_to_process.py`. This is a python script that is used to
generate a list of paths to images. you need to adjust this to point to your
data files.

There is also a subfolder named `parsets` which contains the previously
described parameter set files.


Run the pipeline
================

To start crunshing your data run (from your pipeline folder)::

    $ ./manage.py run <jobname>

Note that you need to supply the database (see `-h`) configuration if you
didn't add it it the `pipeline.cfg` file (or if you are not happy with the
defaults).
