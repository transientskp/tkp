.. _config-overview:

+++++++++++++++++++++++++++++
Configuration System Overview
+++++++++++++++++++++++++++++

Preamble
========

Users organize their Trap runs into *projects*, which contain high-level
descriptions of common Trap parameters. For example, a project specifies which
:ref:`database <database-intro>` to use, and how to connect to a :ref:`Celery
broker <celery-intro>`. All the configuration and log files relating to a
particular project are stored in the same directory hierarchy.

Within a project, the user is able to start multiple pipeline runs, which are
referred to as *jobs*. For example, the user could use a single project to
repeatedly re-analyse a particular set of images with a range of different
sourcefinder settings, with each analysis constituting a particular job.
Alternatively, a project might be dedicated to a multi-epoch survey, with each
job corresponding to a different epoch. The fundamental point is that the
basic control structures such as the database and task distribution system
remain the same, but, within those limits, the user is free to oragnize their
work as they please.

Creating a Project Directory
============================

Use the :ref:`tkp-manage.py <tkp-manage>` to create a project directory::

  $ tkp-manage.py initproject <projectname>

This will create a skeleton directory structure named according to the project
name. Within that directory, there are four files:

``pipeline.cfg``
   The overall pipeline configuration file. This configures the database which
   will be used for this project, as well as specifying where and how to store
   log files. :ref:`See here <pipeline_cfg>` for a full description.

``celeryconfig.py``
   Configuration of the Celery task distribution system.  :ref:`See here
   <celeryconfig_py>` for a full description.

``manage.py``
   An interface to the TKP management system. By default, invoking this is
   functionally equivalent to invoking ``tkp-manage.py``, but it may be
   customized by an end user who requires some pipeline management facility
   that is not provided by default.

``README.md``
   A basic guide to the project directory text format.

Creating a Job
==============

Use the ``manage.py`` script in your project directory to create a job::

  $ cd ./<projectname>
  $ ./manage.py initjob <jobname>

This creates a job directory as a subdirectory of your project directory,
named according to the job name. Within that directory, there are three
files:

``images_to_process.py``
   This defines the list of images which will be processed by this job. It is
   a Python file, which, when loaded, provide at module scope iterable named
   ``images`` which contains the full path to each image to be processed.

   In other words, the file could be as simple as::

     images = ["/path/to/image1", "/path/to/image2", ...]

   Or could contain an elaborate set of globbing and pathname expansion as
   required.

   The end user *will* need to customize to properly specify their
   requirements.

``inject.cfg``
   Configuration for the :ref:`metadata injection tool <tkp-inject>`. This is
   a Python :mod:`ConfigParser` format file.

``job_params.cfg``
   Configuration for each stage of the pipeline run represented by this job.
   This contains all the end-user tunable parameters which are relevant to
   Trap operation. This is a Python :mod:`ConfigParser` format file. Each
   section of the file refers to a particular stage of Trap operation: refer
   to the material on the :ref:`Trap structure <trap-structure>` for a guide
   to the various sections and the relevant configuration parameters.
