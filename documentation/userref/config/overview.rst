.. _config-overview:

+++++++++++++++++++++++++++++
Configuration System Overview
+++++++++++++++++++++++++++++

Preamble
========

Users organize their TraP runs into *projects*, which define the basic
operational TraP parameters, for example which
:ref:`database <database-intro>` to use.
All the configuration and log files
relating to a particular project are stored in the same directory hierarchy.

Within a project, the user is able to configure multiple pipeline runs, which are
referred to as *jobs*. For example, the user could use a single project to
repeatedly re-analyse a particular set of images with a range of different
sourcefinder settings, with each analysis constituting a particular job.
Alternatively, a project might be dedicated to a multi-epoch survey, with each
job corresponding to a different epoch. The fundamental point is that the
basic control structures such as the database and task distribution system
remain the same, but, within those limits, the user is free to organize their
work as they please.

Creating a Project Directory
============================

Use :ref:`tkp-manage.py <tkp-manage>` to create a project directory::

  $ tkp-manage.py initproject <directory-name>

The created directory will contain the following configuration files:

``pipeline.cfg``
   The overall :ref:`pipeline configuration file <pipeline_cfg>`.
   This configures the database which will be used for this project,
   as well as specifying where and how to store log files.
   :ref:`See here <pipeline_cfg>` for a full description.

``celeryconfig.py``
   Configuration of the :ref:`Celery <celery-intro>` task distribution system.
   :ref:`See here <celeryconfig_py>` for a full description.

.. _config-job:

Creating a Job
==============

From within a project directory, use the ``tkp-manage.py`` script to create a job::

  $ cd ./<projectname>
  $ tkp-manage.py initjob <jobname>

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
   Configuration for the :ref:`metadata injection tool <tkp-inject>`.

``job_params.cfg``
   Configuration for each stage of the pipeline run represented by this job.
   This contains all the end-user tunable parameters which are relevant to
   TraP operation. :ref:`See here <job_params_cfg>` for details.

.. _configparser:

Configuration file syntax
=========================

Several of the TraP's configuration files -- :ref:`pipeline.cfg
<pipeline_cfg>`, :ref:`inject.cfg <tkp-inject>`, :ref:`job_params.cfg
<job_params_cfg>` -- use the Python :mod:`ConfigParser` file format. This is
defined by the Python standard library, and you should refer to its
documentation for a comprehensive reference. However, it is worth noting a few
salient points that may be of relevance to the TraP user.

These files are divided into named sections: the name comes at the top of the
section, surrounded by square brackets (``[`` and ``]``). Within a section,
a simple ``name = value`` syntax is used. ``;`` indicates a comment (``#`` may
also be used for commenting, but only at the start of a line).

Variable substiution is performed using the notation ``%(name)s``: this will
be expanded into the value of the variable ``name`` when the file is read.
Variables used in expansion are taken either from the same section of the
file, or from the special ``DEFAULT`` section. For example::

   [DEFAULT]
   a = 1

   [section_name]
   b = 2
   c = %(a)s
   d = %(b)s

Would set the values of ``a`` and ``c`` to ``1``, and ``b`` and ``d`` to
``2``.  In some cases, the TraP provides additional variables which may be
used in expansions in a particular file: these are noted in the documentation
for that file.
