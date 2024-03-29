+++++++++++++++++
Tutorial Overview
+++++++++++++++++

This page walks you through setting up a complete, stand-alone TraP
environment running on your own system.

Install the software
====================

First of all, the software should be installed on your system. See :ref:`the
installation manual <installation>`.

.. note::
    Issues with the `casacore <https://code.google.com/p/casacore/>`_
    installation can occasionally require a per-user fix (placing a small
    config file in your home directory). If you see errors along the lines of::

        WARN    MeasTable::Planetary(MeasTable::Types, Double)
        (file /build/buildd/casacore-1.7.0/measures/Measures/MeasTable.cc, line 4056)
        Cannot find the planetary data for MeasJPL object number 3 at UT day 57023 in
        table DE200

    or::

      SEVERE  gaincal::MeasTable::dUTC(Double) ...
      Leap second table TAI_UTC seems out-of-date.

    Then consult your sysadmin or see :ref:`this note <casacore-measures>`.


``trap-manage.py``
==================
The main tool for configuring and running TraP is :ref:`trap-manage`, which
should be available to you as a command-line utility after installing the TraP.
You may need to consult your sysadmin for details of how to access
your local TraP installation. You can remind yourself of the options available
to you by running::

    $ trap-manage.py -h

Or you can consult the :ref:`documentation <trap-manage>` for details.


Create a pipeline project directory
===================================

To get started using TraP, you should first create a project directory:
this will contain your pipeline settings and job directories.
To create a project folder in your current working directory,
type::

    $ trap-manage.py initproject <projectname>

(substituting ``<projectname>`` for your chosen directory name).

.. _getstart-initdb:

Create a database
=================

The pipeline requires a database for storing data, which needs to be created
manually. The database then needs to be initialised with the TRAP database
schema before it can be used.

Depending on your site configuration, creating a database may require sysadmin
rights. Refer to the documentation on creating a database:

* `PostgreSQL online documentation`_

Initialize a database
=====================

To initialise a database the TraP manage ``initdb`` subcommand can be used.
Set the details of the database you have created in the ``database``
section of your :ref:`pipeline config file<pipeline_cfg>`.
These include the host and port number of
the system running the database management system, the name of the database,
and the username and password.
Then, from the project directory, type::

  $ trap-manage.py initdb


Resetting a TraP database
=========================
You may wish to reset a previously used TraP database to an empty state.

.. warning::
    As you might expect, this may incur irreversible data loss. Be careful!

**PostgreSQL**
  For PostgreSQL there is the optional **-d** flag for the ``initdb`` subcommand,
  which removes all content before populating the database.


Create and configure a job
==========================

Your pipeline project directory can contain multiple jobs, each represented by
a subdirectory. Job directories contain a list of files to process, and config
file that can be used to define various properties used during processing.
To initialise a job directory run::

    $ trap-manage.py initjob <jobname>

This will create a job subdirectory within your pipeline directory. This
directory contains three files:

``images_to_process.py``
    This is a Python script that is used to generate a list of paths to
    images. You will need to adjust this to point to your data files.

``job_params.cfg``
    The :ref:`parameters configuration file <job_params_cfg>` for this job.

``inject.cfg``
    Configuration for :ref:`image metadata injection <tkp-inject>`.

.. _getstart-runpipe:

Run the pipeline
================

To start processing your data, from your pipeline directory run::

    $ trap-manage.py run <jobname>


Position monitoring
--------------------

Additionally you can specify monitoring-locations - TraP will attempt forced-fits
at these co-ordinates, which can help to identify faint sources or place upper
limits on a non-detection. Co-ordinates should be a JSON-format
list of RA,Dec pairs in decimal degrees, either listed at command line::

    $ trap-manage.py run <jobname> -m "[[123,45],[124,46]]"

Or in a JSON-formatted file, e.g.::

    $ cat mycoords.json
        [[123,45],
         [124,46]
        ]

    $ trap-manage.py run <jobname> -l mycoords.json



.. _PostgreSQL online documentation: http://www.postgresql.org/docs/9.1/static/app-createdb.html
