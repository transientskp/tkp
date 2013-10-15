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
  port = 52000
  passphrase =

Check that all the fields match the values given to you by the administrator.
Generally, the ``passphrase`` entry will be blank.

If you wish, you can also customize the other fields in ``pipeline.cfg``:
:ref:`details are here <pipeline_cfg>`. Generally, the defaults are fine.

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

It will also create two configuration files within your subdirectory, the first is
``inject.cfg`` which is used to inject the required metadata into
images which are in the fits format. If you are running the pipeline
on LOFAR images, we recomend using the casa images directly output
from AWImager (with the relevant metadata added). If using fits images
see the main documentation :ref:`here <tkp-inject>` and
talk to an administrator for advice.

The important configuration file is ``job_params.cfg``, which
specifies the settings your pipeline run will use and will require
some initial minor editing described below before you can run the
pipeline. The majority of the default parameters are fine for initial
use, however it is recommended that you check they meet your
requirements. All the parameters are defined in the main documentation
:ref:`here <job_params_cfg>`.

In the ``[persistence]`` section you need to edit the ``description`` of
the file to a recognisable name, this is what your dataset will be
called on the website. Additionally, you will need to comment out
``mongo_host=''localhost''`` and uncomment
``mongo_host=''pc-swinbank.science.uva.nl''``. This will create a fits
copy of your images which can be accessed by the website. The other
parameter which you may wish to use in this parset is
``dataset_id=-1``, this parameter determines the dataset id which
these data will be processed under. -1 is the standard recommended
setting which means that it will simply create a new dataset id by
incrementing the previous dataset id by 1. However, if you want to
include a new set of images in a previously processed dataset, you can
instead specify the previous dataset id here. Note: if you specify a dataset
id here which does not currently exist, your pipeline run will fail.

In the ``[source_extraction]`` section, it is recommended that the option
``force_beam`` is set equal to True (meaning it will cause all the
Gaussians fitted to sources to have the dimensions of the restoring
beam). This parset also requires you to specify the source extraction
region that is appropriate for your images in pixels, you will need to
edit the ``margin`` (a set number of pixels to ignore on the edge of
the image) and the ``radius`` (the radius of the circle in which you
want to extract sources).

The ``[transient_search]`` section contains the different thresholds used
to identify transient sources. The defaults are reasonable, however
you may wish to force all the sources in your sample to be transient
(by setting them all equal to zero, apart from the minpoints)
to check that the defaults are appropriate for your
dataset. Additionally, it can be useful to force the pipeline to only
identify transients which are above the thresholds in a set number of
images by increasing the minpoints (the minimum number of
datapoints required to trigger).


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

For long running jobs (e.g. >1000 images), it is highly recommended
that you run the pipeline from a ``screen``.

While it runs, the pipeline will create the following files in your
job directories:

``<jobname>/*.dump`` - this file is a backup of the content of your
database at the start of your pipeline run. You will need to regularly
remove these files as they may start to take up significant space.

``<jobname>/logs/<date>/jobpars.parset`` - this is a summary of all
the parameters that you set in the parsets for this particular job.

``<jobname>/logs/<date>/output.log`` - a basic log file summarising
the steps completed in your pipeline run. If something goes wrong,
this file is useful for debugging purposes.


View the pipeline results
-------------------------

You can access the results of your pipeline run on the Banana website
here: ``http://banana1.transientskp.org``. Ask an administrator for
the username and password.

If your database can be accessed by the website, its row will be
coloured green. By clicking on the database you can access all your
different pipeline runs. The website provides you with information
about all the transient sources identified, all the sources available
in the database, the individual extracted sources and information
about each image. Most of the figures are interactive - allowing you to
zoom in, select which frequencies to plot, save/print versions of the
plots, identify sources in the image, etc... Additionally, most of the
tables can be sorted by different columns and downloaded in csv
format.

Understanding the pipeline results
----------------------------------

The transient list obtained contains two different types of transient
sources: sources whose transient parameters exceed the thresholds stated
in the ``[transient_search]`` section of the ``job_params.cfg`` file
and new sources which were not present in a previous image of the field.

In Release 1 of the pipeline, the new sources typically dominate the
transient list and are mostly not real transients. This is because the
new source was typically just below the detection threshold in the
first image and is, therefore, not a real transient. You will need to
manually check through the new sources to look for real transients,
i.e. those which you would have expected to detect in the first
image. In Release 2 of the pipeline, this will be completed
automatically for you.
