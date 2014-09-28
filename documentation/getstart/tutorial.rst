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


Create a pipeline project directory
===================================

First, create a project directory: this will contain your pipeline settings and
job directories. To create a project folder in your current working directory,
type::

    $ tkp-manage.py initproject <projectname>

(substituting ``<projectname>`` for your chosen directory name).

.. _getstart-initdb:

Create a database
=================

The pipeline requires a database for storing data, which needs to be created
manually. The database then needs to be initialised with the TRAP database
schema before it can be used.

Depending on your site configuration, creating a database may require sysadmin
rights. Refer to the relevant documentation for your installed database engine
on creating a database:

* `MonetDB online documentation`_
* `PostgreSQL online documentation`_

Initialize a database
=====================

To initialise a database the TraP manage ``initdb`` subcommand can be used.
Set the details of the database you have created in the ``database``
section of your :ref:`pipeline_cfg`. These include the host and port number of
the system running the database management system, the name of the database,
and the username and password.
Then, from the project directory, type::

  $ tkp-manage.py initdb


Resetting a TraP database
=========================
You may wish to reset a previously used TraP database to an empty state.

.. warning::
    As you might expect, this may incur irreversible data loss. Be careful!

**PostgreSQL**
  For PostgreSQL there is the optional **-d** flag for the ``initdb`` subcommand,
  which removes all content before populating the database.

**MonetDB**
  In the case of MonetDB you need to do this manually. You can do this with the
  following commands, where **${dbname}** should be replaced with the database
  name::

    monetdb stop ${dbname}
    monetdb destroy -f ${dbname}
    monetdb create ${dbname}
    monetdb start ${dbname}
    monetdb release ${dbname}

  For security reasons you should change the default password::

    mclient -d ${dbname} -s"ALTER USER \"monetdb\" RENAME TO \"${username}\";
    ALTER USER SET PASSWORD '${password}' USING OLD PASSWORD 'monetdb';"


Create and configure a job
==========================

Your pipeline project directory can contain multiple jobs, each represented by
a subdirectory. Job directories contain a list of files to process, and config
file that can be used to define various properties used during processing.
To initialise a job directory run::

    $ tkp-manage.py initjob <jobname>

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

To start processing your data run (from your pipeline directory)::

    $ tkp-manage.py run <jobname>


.. _MonetDB online documentation: https://www.monetdb.org/Documentation/monetdbd
.. _PostgreSQL online documentation: http://www.postgresql.org/docs/9.1/static/app-createdb.html