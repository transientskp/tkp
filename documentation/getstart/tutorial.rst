+++++++++++++++++
Tutorial Overview
+++++++++++++++++

This page walks you through setting up a complete, stand-alone TraP
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
the TraP manage ``initdb`` subcommand can be used (from the project directory)::

  $ ./manage.py initdb

Use the ``-h`` flag to see an explanation about how to set the various
properties. They can also be configured throught the :ref:`pipeline_cfg`. Note
that the semantics vary slightly depending on the database system in use: see
the :ref:`database documentation <database-section>` for details.

Create and configure a job
==========================

Your pipeline project directory can contain multiple jobs. Jobs are a list of
files to process, and a set of "parset" (parameter set) files that can be used
to define various properties used during processing. To initialise a job run::

    $ ./manage.py initjob <jobname>

This will create a job subdirectory within your pipeline directory. This
directory contains three files:

``images_to_process.py``
    This is a Python script that is used to generate a list of paths to
    images. You will need to adjust this to point to your data files.

``job_params.cfg``
    The :ref:`parameters configuration file <job_params_cfg>` for this job.

``inject.cfg``
    Configuration for :ref:`image metadata injection <tkp-inject>`.


Run the pipeline
================

To start crunshing your data run (from your pipeline directory)::

    $ ./manage.py run <jobname>

Note that you need to supply the database (see ``-h``) configuration if you
didn't add it it the ``pipeline.cfg`` file (or if you are not happy with the
defaults).
