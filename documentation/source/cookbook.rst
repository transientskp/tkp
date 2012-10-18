.. _cookbook:

Transients Pipeline Cookbook
============================

.. |last_updated| last_updated::

*This document last updated:* |last_updated|.

.. warning::

   The information in this page is old and, in places, outdated.

This section deals with a simpe, standard way of getting the Trap running. It
assume you are working on the ``heastro`` compute machine in Amsterdam.

Firstly, it's best to *unset* your :envvar:`PYTHONPATH` and
:envvar:`LD_LIBRARY_PATH`, so you have a clean environment; the pipeline setup
takes care of these environment variables. Besides, on ``heastro``, most
dependencies like wcslib, pyrap, hdf5 are installed in system directories and
will be picked up automatically.

This document does *not* describe runnign the "Trip" (a putative imaging
pipeline developed for Transients use). This pipeline is currently deprecated.
Start the Trap using (FITS) image files for now.

Setting up the directory structure and configuration files
----------------------------------------------------------

This must currently be done manually, as the ``trapinit.py`` script has been
deprecated. It is suggested that you find somebody with an existing
configuration which you can adapt.

Checking and editing the various configuration files
----------------------------------------------------

Create the file :file:`images_to_process.py` in the
control directory. This contains a list of images to process::

    images = [
    '/home/evert/scratch/bell/L09851_227sbs.fits',
    '/home/evert/scratch/bell/L09936_227sbs.fits',
    '/home/evert/scratch/bell/L09948_227sbs.fits',
    '/home/evert/scratch/bell/L20033_227sbs.fits',
    '/home/evert/scratch/bell/L20613_227sbs.fits',
    ]

Note that the images are processed in the order they are listed, which
most logically would be in time order. Note that you can pick any
preferred job name (the :option:`-j` option in :file:`runtrap.sh`),
which is what gets entered into the database for these images.

Create the :file:`runtrap.sh` file, containing something like the following::

    #! /bin/sh

    # Uncomment the following four lines if you want to remove old stuff
    # Only do this automatically when testing
    #rm -r /zfs/heastro-plex/scratch/evert/trap/L2010_21641/*
    #rm -r /home/evert/pipeline-runtime/jobs/L2010_21641/control/vds/*
    #rm -r /home/evert/pipeline-runtime/jobs/L2010_21641/control/results/*
    #rm /home/evert/pipeline-runtime/jobs/L2010_21641/statefile

    CONTROLDIR=/home/evert/pipeline-runtime/jobs/L2010_21641/control
    # Note! The next command spans 3 lines
    PYTHONPATH=/opt/tkp/tkp/lib/python:/opt/LofIm/lofar/lib/python2.6/dist-packages:/opt/monetdb/lib/python2.6/site-packages:/opt/pipeline/framework/lib/python2.6/site-packages \
    LD_LIBRARY_PATH=/opt/tkp/tkp/lib:/opt/LofIm/lofar/lib/python \
    python ${CONTROLDIR}/trap-images.py -d --task-file=${CONTROLDIR}/tasks.cfg -j L2010_21641 -c /home/evert/pipeline-runtime/sip.cfg $1

This file sets up the environment to start the pipeline, and then
starts it with the correct arguments. It's the file you would normally
run to get the pipeline started. There are some commented lines that
take care of cleaning up in case you want a completely fresh start of
the pipeline. Remember that the :file:`statefile` keeps the current
state of the pipelin, so in case you interrupt it halfway or you come
across a bug in a recipe that can be easily fixed, you can restart the
pipeline at the point, without completely needing to restart afresh.

The actual :file:`trap-images.py` is the main recipe. You should copy this
from the main recipe directory to your ``control`` directory and edit it as
you see fit. Normally, you shouldn't have to change it.

Then, there are a bunch of configuration files. First up is
:file:`${HOME}/.tkp.cfg`, the TKP configuration file. If you didn't
have one already (in the above example, I had one already, so none was
created), a new, very basic config file is created. Most important
part to check here are the database login details. By default, this is
`tkp`, but you may want to use a different database.

Then, there is the sip configuration file, :file:`sip.cfg`, which
holds the configuration details for the pipeline framework. Most
values there should be fine, but always check. Keep in mind that the
TKP recipes directories needs to come before the pipeline recipes
directory::

    recipe_directories = [/opt/tkp/tkp/recipes, /opt/pipeline/recipes]

to avoid conflicts with identically named recipes.

Then, there is :file:`tasks.cfg` in the control directory. This
contains a lot of settings that you may want to play around with,
especially for the TRAP part: instead of parsets, the TRAP uses this
file to set most of its parameters. For example, the source detection
level is set there, as are the association radius and the level above
which a light curve is considered "transient". Another interesting
recipe is the `time_slicing` recipe, which splits up the input
measurement set into smaller chunks (although the default of twelve
hours usually means is it one big chunk). This does mean that there
will be subdirectories in the working data directory and the results
directory, with their names according to the start time in Unix
seconds (seconds since January 1, 1970, which is the internal
convention for measurement sets).

Some more details on the individual recipes can be found in the
:ref:`corresponding section <recipes-section>`.

An important parameter in :file:`tasks.cfg` is the `nproc` parameter:
it sets the number of processes run simultaneously on a single compute
node. In optimal cases, you may want to set this to the number of
cores per compute node, but if other people are also busy on the same
cluster, you may want to set it to a value like 2 or 3. By default, it
is safely set to 1.

Finally, check if the cluster description file satisfies your needs
(on CEP 1, the default will only use cluster 3, the imaging cluster),
and alter the parset files as seen fit (for details on this, use
e.g. the imaging cookbook).
