#################
Setup
#################
.. |last_updated| last_updated::

:Last updated: |last_updated|

.. warning::

   The workflow described here has been largely superseded by the
   ``trap-manage`` script - documentation for which is coming soon.

Preamble
--------

A few variables are used in the documentation below, indicating
relevant directories that may differ from system to system:

- :envvar:`${TKP}`: the base TKP directory on your system. On the heastro
  machines, this would be :file:`/opt/tkp/tkp`.

- :envvar:`${WORK}`: your working directory for the pipeline, that is, where
  the jobs control is kept. You can store this were you like, often in
  :file:`${HOME}/pipeline_runtime`. This directory contains the :file:`jobs/`
  subdirectory and, optionally, the :file:`trap.cfg` as well.

- :envvar:`${CONFIG}`: the main configuration file for the pipeline framework.
  It contains sections such as ``[DEFAULT]``, ``[layout]``, ``[cluster]``,
  ``[deploy]`` and ``[logging]``.

- You will also need a TKP configuration file that has the database
  login details, unless you can rely upon the default (below), The TKP
  configuration should be :file:`${HOME}/.tkp.cfg`, and has the same syntaxa
  as the other pipeline configuration files. The default configuration
  for the pipeline looks as follows::

    [database]
    enabled = True
    host = ldb001
    name = tkp
    user = tkp
    password = tkp
    port = 50000


On heastro
----------

The necessary TKP libraries are installed in :file:`/opt/tkp/latest`.  The
last part of this path is a symbolic link to a nightly build in
:file:`/opt/tkp/yyyy-mm-dd-hh-mm/`; use a specific nightly build if you have
long-running jobs or need a specific TKP library version.


Within the :file:`/opt/tkp/latest` directory, there are two subdirectories:
:file:`lib/` and :file:`bin/`. The former contents the required TKP libraries
and also all the Trap recipes; the latter contains stand-alone scripts which
may be helpful in managing your pipelines.

Your :envvar:`PYTHONPATH` and the ``ppath`` variable in your main
configuration file will need to include the
:file:`lib/pythonX.Y`, with `X.Y` being the version of Python in use on your
system (2.6 at present on ``heastro1``). You will also need to include
:file:`/opt/LofIm/lofar/lib/python2.6/dist-packages` to pick up the LOFAR
pipeline framework.

Other dependencies are system-wide installed.

Your ``lpath`` in your configuration file needs to include:

- :file:`/opt/LofIm/lofar/lib`

- :file:`/opt/tkp/latest/lib`


Now set up your working directory structure and configuration files in
the usual pipeline way.  Example configuration files can be copied and
adjusted from :file:`/home/evert/work/trap/trap.cfg` and
:file:`/home/evert/work/trap/jobs/example/control/tasks.cfg`.

The recipes directory,
:file:`${TKP}/lib/python2.6/site-packages/trap/recipes`, contains practical
recipes for the TRAP; these are in the master and nodes subdirectories
(frontend and compute node recipes). The SIP recipes can be found in
:file:`/opt/LofIm/lofar/lib/python2.6/dist-packages/lofarpipe/recipes`, but
some of these have a slightly adjusted variant in the TKP recipes directory.
The main TKP recipes directory also contains an example `trap-images.py`
recipe which takes a list of images as input and searches them for transients.

It is assumed you know how to edit the :file:`trap.cfg` and :file:`tasks.cfg`
files, as well as set up parset and other files. For simplicity,
however, the example files mentioned in the :ref:`recipes section
<recipes-section>` can be used.


.. _heastro-simple-way:

Simple way
~~~~~~~~~~

(For simplicity, me, myself and I in the following will simply refer to the
current author of this document.)

This describes a copy-paste way to get the trap running on heastro1 or
heastro2, essentially by copying my setup and adjust a few PATHs
accordingly. The PATH set up is done slightly different than the
previous section, but in essence is the same.

Firstly, lay out the usual pipeline directory structure::

    $HOME/work/trap/jobs/<job-id>

where job-id is probably named after the dataset you want to process.

Copy the directory and subdirs from ``~evert/work/trap/jobs/example/`` into this directory::

    cp -r ~evert/work/trap/jobs/example/*  $HOME/work/trap/jobs/<job-id>/.

And copy the trap configuration file::

    cp -r ~evert/work/trap/trap.cfg  $HOME/work/trap/trap.cfg

You should now have the following structure::

    $HOME/work/trap/trap.cfg
    $HOME/work/trap/jobs/<job-id>/
                                  control/
                                  parset/
                                  vds/
                                  results/
                                  logs/

The results, logs and vds directories will be empty.

Now edit trap.cfg. Only a few edits will be necessary. In particular, check:

- ``runtime_directory``

- ``lofarroot``

- ``default_working_directory``

You can use my cluster description file and recipes directories.  If
you have your own MonetDB database, change the login details in the
``[database]`` section accordingly, otherwise use mine or the default
scratch one: tkp/tkp/tkp.


Now edit :file:`control/runtrap.sh`. This is a simple script that
first clears directories (since the pipeline won't clobber existing
files normally), and then runs the TRAP with the correct job ID. Edit
the paths accordingly. Don't forget to change the job name (value to
-j option) as well!

Now edit the :file:`control/tasks.cfg` file as necessary. In
particular, pay attention to the database credentials: for BBS, set
``db_name`` to your user name; for the skymodel databse (MonetDB), you
can use the tkp/tkp/tkp scratch database, or the default I'm using.

Last things to edit are the :file:`control/to_process.py` or
:file:`control/images_to_process.py` files and the various
parsets. Once you are happy with all settings, you can run the trap
with::

    ./runtrap.sh

Additional setup
----------------

Passwordless ssh
~~~~~~~~~~~~~~~~

When using the pipeline over the cluster, it generally uses ssh connections.
Since you do not want to type in your password for every connection it makes,
you create authorization keys with a blank password (if you find that insecure,
you can also use something like ssh-agent to store the password. On most
clusters, however, the security comes from your initial login to the frontend
node anyway). To do this::

    $> ssh-keygen -t dsa

Enter a blank password (just press return). Then::

    $> cat ~/.ssh/id_dsa.pub >> ~/.ssh/authorized_keys

Since the `.ssh` directory is located in your home directory, the
`authorized_keys` file is available on all cluster nodes, and you should now
have a passwordless login to every cluster node.

You also want to disable the host key check that ssh performs every first time
you log in to a node. You can do that by setting StrictHostKeyChecking to
'no'::

    $> cat >> ~/.ssh/config
    StrictHostKeyChecking no
    <ctrl-D>
