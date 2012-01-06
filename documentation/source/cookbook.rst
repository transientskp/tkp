.. _cookbook:

Transients Pipeline Cookbook
============================

This section deals with a simpe, standard way of getting the TRAP (and
the TRIP if necessary) running. It assume you are working on one of
the Amsterdam heastro nodes, although it possibly may work on CEP 1 as
well (untested as per 2011-08-31).

Firstly, it's best to *unset* your :envvar:`PYTHONPATH` and
:envvar:`LD_LIBRARY_PATH`, so you have a clean environment; the
pipeline setup takes care of these environment variables. Besides, on
heastro, most dependencies like wcslib, pyrap, hdf5 are installed in
system directories and will be picked up automatically (on CEP 1, you
will need to set your :envvar:`LD_LIBRARY_PATH`; the TRAP
initialisation script should tell you which paths to add).


Setting up the directory structure and configuration files
----------------------------------------------------------

Locate the TKP directory (the evelopment version); on heastro, it's
in :file:`/opt/tkp/tkp`. On CEP 1, it's in
:file:`/home/rol/tkp/tkp`.  In the :file:`bin` subdirectory,
you'll find the TRAP initialisation script: :file:`trapinit.py`.

Run :file:`trapinit.py`::

    $> python trapinit.py

It will try and determine your setup, and check if various Python
modules could be loaded. Then, it asks you a bunch of questions; the
first questions deals with your overall working directory. By default,
this is :file:`${HOME}/pipeline-runtime`, but if you already have this
directory, it may be safer to pick a new directory. The script is
smart enough to not overwrite existing directories and files, but if
you create a directory from scratch, you can actually see what it has
all created.

Most of the questions can be answered using their defaults. At some
point, the script will ask you about the dataset that you want to run
the TRAP (and possibly TRIP) on. This can be any name, but there is an
advantage if you name it after the name it has on the storage
node(s). For the heastro machines, looke in
:file:`/zfs/heastro-plex/archive/`. For now, let's use
L2010_20850_1. At the very end of the script, you have the option of
letting the init script find the various data files (subbands) for
you. This usually works fine on heastro (if you follow the dataset
naming convention mentioned before); on CEP 1 you may need to edit the
:file:`ms_to_process.py` manually (but it's always good to inspect
this file anyway!).

A complete run could look like this::

    $> python trapinit.py
    Determining default setup
    
    Checking modules
    
    The following setup has been detected on the system:
    TKP / TRAP main directory:        /opt/tkp/tkp
    Database (MonetDB) python module: /opt/monetdb/lib/python2.6/site-packages
    Pipeline framework:               /opt/pipeline/framework/lib/python2.6/site-packages
    LofIm main directory:             /opt/LofIm/lofar
    Working (scratch) data directory: /zfs/heastro-plex/scratch/evert/trap
    
    Enter the pipeline runtime directory (/home/evert/pipeline-runtime)? /home/evert/trap-runtime
    Directory /home/evert/trap-runtime does not exist.
    Create directory (YES/no)? 
    Directory /home/evert/trap-runtime/jobs does not exist.
    Create directory (YES/no)? 
    Enter the working scratch directory (/zfs/heastro-plex/scratch/evert/trap)? 
    No cluster description file detected
    Would you like to have a default one created (YES/no)? 
    Created default cluster description file /home/evert/trap-runtime/heastro.clusterdesc
    No SIP configuration file detected
    Would you like to have a default one created (YES/no)? 
    Created default SIP configuration file /home/evert/trap-runtime/sip.cfg
    Create a job directory structure for a new dataset (YES/no)? 
    Dataset name? L2010_20850_1
    Create default parsets (YES/no)? 
    Try to find subbands based on dataset name (YES/no)? 
    
    The following files have been created.
    You may want to review and edit them:
      /home/evert/trap-runtime/jobs/L2010_20850_1/parsets/ndppp.1.parset
      /home/evert/trap-runtime/sip.cfg
      /home/evert/trap-runtime/jobs/L2010_20850_1/control/tasks.cfg
      /home/evert/trap-runtime/heastro.clusterdesc
      /home/evert/trap-runtime/jobs/L2010_20850_1/parsets/bbs.parset
      /home/evert/trap-runtime/jobs/L2010_20850_1/control/ms_to_process.py
      /home/evert/trap-runtime/jobs/L2010_20850_1/control/runtrap.sh
      /home/evert/trap-runtime/jobs/L2010_20850_1/parsets/mwimager.parset
      /home/evert/trap-runtime/jobs/L2010_20850_1/parsets/ndppp.2.parset
    $>


Checking and editing the various configuration files
----------------------------------------------------

As you see, the script will tell you which files have been created
(and implicitly which directories). As suggested, we review a few of
those files. Let's start with the :file:`ms_to_process.py` file, which
may look something like::

    datafiles = [
        '/zfs/heastro-plex/archive/L2010_21641/processed/L21641_SB000_uv.MS.dppp',
        '/zfs/heastro-plex/archive/L2010_21641/processed/L21641_SB001_uv.MS.dppp',
        '/zfs/heastro-plex/archive/L2010_21641/processed/L21641_SB002_uv.MS.dppp',
        .
        .
        .
        '/zfs/heastro-plex/archive/L2010_21641/processed/L21641_SB220_uv.MS.dppp',
    ]

These are, presumably, the files you want to process: first through
the TRIP, then through the TRAP (the .dppp extension indicates they
have at least been compressed, but the data are otherwise
unflagged). The format is that of a simple Python list, since the file
itself is, in fact, a very simple Python module that is read by the
main recipe (see below). For a first try-out, you may want to comment
out most of the file names, and just keep only a few files to run
through the pipeline.


Then the :file:`runtrap.sh` file::

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
    python ${CONTROLDIR}/trap-with-trip.py -d --task-file=${CONTROLDIR}/tasks.cfg -j L2010_21641 -c /home/evert/pipeline-runtime/sip.cfg $1

This file sets up the environment to start the pipeline, and then
starts it with the correct arguments. It's the file you would normally
run to get the pipeline started. There are some commented lines that
take care of cleaning up in case you want a completely fresh start of
the pipeline. Remember that the :file:`statefile` keeps the current
state of the pipelin, so in case you interrupt it halfway or you come
across a bug in a recipe that can be easily fixed, you can restart the
pipeline at the point, without completely needing to restart afresh.

The actual :file:`trap-with-trip.py` is the main recipe, and is copied
from the TRAP recipes main directory to the control
directory, so you can edit this file as you see fit. Normally, you
wouldn't really need to.

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


Running the TRAP
----------------

If you're satisfied with the various settings, let's get started. Move
into the :file:`control` subdirectory and start the runtrap script::

    >$ sh runtrap.sh

That should be enough to keep the system churning away for a while on
the data. The TRIP part will take up most of the time. Once the
flagging and calibration part is done, the main recipe will enter a
loop, where an image is formed for a certain time slice (that is, the
imager is run for each subband and then subbands are combined into one
final image), sources are detected, transients are searched and
possibly classification are done for the transients.


Running the TRAP when you already have images
---------------------------------------------

It may be the case that you already have a set of images, and you want
to run the TRAP on that set of images. No flagging, calibration,
imaging or time slicing is necessary in that case.

For that, copy the recipe :file:`trap-images.py` into the control
directory, and created a file :file:`images_to_process.py` in the
control directory. The latter file is very similar to
:file:`ms_to_process.py`, but this time contains a list of images
instead of measurement sets::

    images = [
    '/home/evert/scratch/bell/L09851_227sbs.fits',
    '/home/evert/scratch/bell/L09936_227sbs.fits',
    '/home/evert/scratch/bell/L09948_227sbs.fits',
    '/home/evert/scratch/bell/L20033_227sbs.fits',
    '/home/evert/scratch/bell/L20613_227sbs.fits',
    ]

Now replace `trap-with-trip.py` with `trap-images.py` in your
:file:`runtrap.sh` and run the pipeline as usual::

    >$ sh runtrap.sh

Note that the images are processed in the order they are listed, which
most logically would be in time order. Note that you can pick any
preferred job name (the :option:`-j` option in :file:`runtrap.sh`),
which is what gets entered into the database for these images.
