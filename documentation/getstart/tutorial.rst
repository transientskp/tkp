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

Configure the ephemeris
=======================

Note that as part of the installation you (or your system administrator) will
have installed the casacore "measures data". This includes information
essential to carrying out astronomical calculations, such as a list of leap
seconds and a set of solar system ephemerides (which specify the positions of
the planets at any given time). Data for the ephemerides are ultimately
supplied by `NASA JPL`_; they have been converted into a format that casacore
can use. Any given ephemeris is only valid for a limited time (usually on the
order of centuries), determined by the accuracy with which it was calculated.

By default, casacore will use the ``DE 200`` ephemeris. Although the version
of ``DE 200`` supplied by JPL is valid until 2169, *some versions converted
for use with casacore are not*, and may not provide coverage of the dates of
your observation. A simple Python script can be used to check::

  $ cat check_ephemeris.py
  import sys
  from  pyrap.measures import measures
  dm = measures()
  dm.do_frame(dm.epoch('UTC', sys.argv[1]))
  dm.separation(dm.direction('SUN'), dm.direction('SUN'))
  $ python check_ephemeris.py 1990/01/01
  $ python check_ephemeris.py 2015/01/01
  WARN    MeasTable::Planetary(MeasTable::Types, Double)
    (file /build/buildd/casacore-1.7.0/measures/Measures/MeasTable.cc, line 4056)
    Cannot find the planetary data for MeasJPL object number 3 at UT day 57023 in
    table DE200

If no warning is printed, there is no problem; otherwise, you should use a
different ephemeris. For example, the ``DE 405`` ephemeris should be valid
until at least early 2015::

  $ cat > ~/.casarc
  measures.jpl.ephemeris: DE405
  $ python check_ephemeris.py 2015/01/01
  # No warnings

.. _NASA JPL: http://iau-comm4.jpl.nasa.gov/README.html

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
