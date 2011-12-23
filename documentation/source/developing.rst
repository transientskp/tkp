++++++++++++++++++++++++++++++++++++++
Developing for the Transients Pipeline
++++++++++++++++++++++++++++++++++++++

This documents deals (shortly) with writing software for the
Transients Pipeline, either the TraP part (recipes) or the underlying
modules (the TKP package).

TraP
----

The Transients Pipeline is formed by a set of master-node recipes
within the standard pipeline framework. Each master recipe is in
essence a single step in the pipeline (though occasionally, steps will
be combined), and may or may not drive a set of distributed compute
node recipes. Master recipes derive from a
:class:`lofarpipe.support.baserecipe.BaseRecipe`, and when a master
recipe needs to start up compute node recipes, from
:class:`lofarpipe.support.remotecommand.RemoteCommandRecipeMixIn` as
well. Compute node recipes generally are derived from
:class:`lofarpipe.support.lofarnode.LOFARnodeTCP`. The master recipes
know how to import the compute node recipes from the logic that the
node recipes live in the :file:`../nodes/` subdirectory with the same
name as the master recipe (the master recipe lives, of course, in the
:file:`../master/` subdirectory.

The inputs (parameters) and outputs (results; return values) of the
master recipe are given by two class variables, and are used in the
main `go` method. Normally, the `go` method is the only method that
needs to be overridden in the derived master recipe. Inputs can be
given when calling the recipe, often from another (main) recipe, using
the `run_task` method; the outputs are returned as a dictionary from
the same `run_task` method. Note that the recipes themselves should
always return 0 on success and non-0 on failure.

The node recipes are simpler. They don't require inputs and outputs to
be defined and just take their arguments in the `run` method, which is
the method to be overridden from the base node recipe (eg,
:class:`LOFARnodeTCP`). The return value is again 0 or non-0; the
actual results are stored in the `outputs` attribute.

The node recipes are called from the master recipe using the
:class:`ComputeJob` class. This sets up the call to the node recipe
with the correct argument, and includes the compute node this recipe
will be run on. A list of compute nodes is obtained from the cluster
description file, and iterating through them, one creates several
:class:`ComputeJob` instances, which are then scheduled and run.

A simplified example (from the classification recipe) looks as follows
(note that the import statements are not shown, nor are the inputs and
outputs definitions)::

    def go(self):
        super(classification, self).go()
	# Obtain the available compute nodes
        clusterdesc = ClusterDesc(self.config.get('cluster', "clusterdesc"))
       available_nodes = {
            clusterdesc.name: get_compute_nodes(clusterdesc)
            }
        nodes = list(itertools.chain(*available_nodes.values()))
        # Set up the command to be run on the compute nodes, as a python script over ssh
        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        nodes = itertools.cycle(nodes)
        for transient in transients:
            node = nodes.next()
            self.logger.info("Executing classification for %s on node %s" % (transient, node))
            jobs.append(
                # Create a compute job, on this node with the given command and list of arguments
                ComputeJob(node, command, arguments=[
                self.inputs['schema'], self.config.get("layout", "parset_directory"),
                transient, weight_cutoff, tkp.config.CONFIGDIR]))
        self.logger.info("Scheduling jobs")
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])  # nproc limits the maximum amount of CPU allowed to be used
	# Get the results
        self.outputs['transients'] = [job.results['transient'] for job in jobs.itervalues()]
        # Check if we got any error from running the jobs
        if self.error.isSet():
            return 1
        else:
            return 0


Keep in mind that a master recipe does not have to call a compute node
recipe (which then eliminates all of the above code). For example, the
`transient_search` recipe consists only of a master recipe: any
computational intensive work is actually done on the database, and the
overhead of starting up a compute node to interact with the database
is probably more than calling the database directly from the master
(front end) node.


A note on database connections: these cannot be transferred from the
master to the node recipes (cannot be pickled, and thus cannot be
transferred across the ssh connection), so each compute node has to
open its own database connection, and close it again. The most obvious
way (if the TKP configuration file is configured for the correct
database) is simply using::

    from contextlib import closing
    def run(self, *args):
        with log_time(self.logger):
            with closing(DataBase()) as database:
	        pass


TKP
---

The TKP package is a set of modules (or actually modules within four
subpackages) that implement the algorithms used by the transients
pipeline. The subpackages are:

- database

- sourcefinder

- classification

- utility

The names of the subpackages should speak for themselves; utility is
more or less a collection of code that does not really fit anywhere
else, or ties a few subpackages together (such as the database and
sourcefinder).

The main thing to keep in mind when writing (new) code is that the
subpackages are, as much as possible, independent of each other. There
are some minor dependencies still among the packages, but these will
hopefully be removed in the future. Other than that, the individual
module names should give one a good idea what code to put where. An
overview of the most used modules and a short description of their
task follows:

- database

  - database: take care of database connection

  - dataset: mini-ORM to some database tables

  - utils: all the SQL queries inside their respective Python functions

- sourcefinder

  - image: image (data) handling through the Image class

  - extract: source extraction routines

  - fitting: actual source fitting routines

  - gaussian: 2D gaussian function 

  - stats: specific statistic routines

  - utils: some sourcefinder specific utilities

- classification

  - manual: subpackage for manual classification

    - transient: define transient class

    - classifier: classifier routines

    - classification: defines the classification (decision tree); can be user overriden

    - utils: utility classes for the transient class

  - features: feature detection subpackage

    - lightcurve: obtain characteristics of the transient light curve

    - catalog: catalog (position) matching routines

    - sql: SQL routines (to be integrated into the lightcurve module)

- utility:

  - accessors: (Image) data file handling classes

  - containers: classes for handling the sourcefinder results

  - coordinates: various coordinate handling routines, and WCS class

  - fits: few routines to handle MS to FITS metadata and combination (stacking) of FITS files

  - memoize: decorator to cache results of methods

  - sigmaclip: generic kapp, sigma clipping routine (used by classification.features)

  - uncertain: Uncertainty class that can hold a value plus its errors

  - exceptions: a few (rarely used) TKP exception classes



Coding guideline
----------------

We try to follow PEP 8 as much as possible, although at times, this is
flexible (e.g., short variable names sometimes make more sense in the
context; and there is no hard rule where braces or parentheses should
go when they cover more than one line).

Occasionally, it may be useful to run pylint (or similar) on the code,
to pick out a few things (unused variables and such). Don't aim to get
a 10/10 score, just use the suggestions by pylint where deemed
applicable.



Documentation
=============

All documentation in the `code` part of the TKP repository is written
in restructured text, whether doc strings or longer documents, and is
then put together and transformed using Sphinx. By 'put together', we
mean that Sphinx will pick up the doc strings from referenced modules
and add this to the other documentation; by transformed we mean the
Sphinx will create HTML pages out of the documentation. The latter is
done on a nightly basis, so that documentation is refreshed over
night.

There currently exists two main sections of documentation:

- TraP: this section deals with setting up and running the transients
  pipeline, as well as more details about the individual recipes.

- TKP: this section deals with the underlying modules and algorithms
  used in the transients pipeline.


Doc strings
-----------

The doc strings also follow pretty much the suggestions in PEP 8. They
are relatively relaxed, and not all methods will have a proper
docstring. The documentation of the arguments and keyword arguments
follow roughly the convention suggested `by Google
<http://google-styleguide.googlecode.com/svn/trunk/pyguide.html?showone=Comments#Comments>`_
(`see also
<http://packages.python.org/an_example_pypi_project/sphinx.html#function-definitions>`_).




Testing
=======

Unit tests
----------

Pipeline tests
--------------


