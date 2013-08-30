Introduction
============

This is a TRAP pipeline runtime folder. From here you can start and manage
your TRAP jobs. For more info, visit the TRAP documentation website:

 * http://docs.transientskp.org/


usage
=====

preperations
------------

First make sure your environment variables are correct. These are different
per system. For heastro1 they are:

    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/wcslib/lib:/opt/casacore/lib:/opt/pyrap/lib
    PATH=${PATH}:/opt/tkp/latest/bin
    PYTHONPATH=${PYTHONPATH}:/opt/tkp/latest/lib/python2.6/site-packages/:/opt/LofIm/lofar/lib/python2.6/dist-packages/

You can add this to your bash configuration (~/.bashrc) for example.


Initialisation
--------------

To create a TRAP pipeline runtime:

 $ trap-manage.py initproject <projectname>

Which will create a folder named <projectname> in the current folder. In this
folder is a manage.py script, which is just a copy of the trap-manage.py
script.


Create a job
------------

To create a job, run (in your pipeline folder):

 $ ./manage.py initjob <jobname>

This will create a subfolder called <jobname>, which contains a files called
*images_to_process.py*. This file is a python script which should define
variable *images* which defines a list of paths to images to process for this
job. Also it contains a directory *parsets* which contains all the parameter
files for each TKP recipe. These values can be adjusted to your needs.


Run a job
---------

To run a specific job run:

 $ ./manage.py run <jobname>


Files
=====

* *pipeline.cfg*
  configuration file for this pipeline. For syntax info see:
  <http://docs.python.org/library/configparser.html>

* *example.clusterdesc*
  an example cluster description, only required if you want to setup your
  own (test) distributed invironment




