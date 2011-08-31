Transients Pipeline Cookbook
============================

This section deals with a simpe, standard way of getting the TRAP (and
the TRIP if necessary) running. It assume you are working on one of
the Amsterdam heastro nodes, although it possibly may work on CEP 1 as
well (untested as per 2011-08-31).

Firstly, it's best to *unset* your PYTHONPATH and LD_LIBRARY_PATH, so
you have a clean environment; the pipeline setup takes care of these
environment variables. Besides, on heastro, most dependencies like
wcslib, pyrap, hdf5 are installed in system directories and will be
picked up automatically (on CEP 1, you will need to set your
LD_LIBRARY_PATH; the TRAP initialisation script should tell you which
paths to add).


Locate the TKP directory (the development version); on heastro, it's in /opt/tkp/dev/tkp. On CEP 1, in /home/rol/tkp/dev/tkp.
In the `bin` subdirectory, you'll find the TRAP initialisation script: `file:trapinit.py`.
Run `file:trapinit.py`::

    python trapinit.py

It will try and determine your setup, and check if various Python modules could be loaded. Then, it asks you a bunch of questions; the first questions deals with your overall working directory. By default, this is `file:${HOME}/pipeline-runtime`, but if you already have this directory, it may be safer to pick a new directory. The script is smart enough to not overwrite existing directories and files, but if you create a directory from scratch, you can actually see what it has all created.

Most of the questions can be answered using their defaults. At some point, the script will ask you about the dataset that you want to run the TRAP (and possibly TRIP) on. This can be any name, but there is an advantage if you name it after the name it has on the storage node(s). For the heastro machines, looke in /zfs/heastro-plex/archive/. For now, let's use L2010_20850_1. At the very end of the script, you have the option of letting the init script find the various data files (subbands) for you. This usually works fine on heastro (if you follow the dataset naming convention mentioned before); on CEP 1 you may need to edit the ms_to_process.py manually (but it's always good to inspect this file anyway!).

A complete run could look like this::

    $> python trapinit.py
    Determining default setup
    
    Checking modules
    
    The following setup has been detected on the system:
    TKP / TRAP main directory:        /opt/tkp/dev/tkp
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

