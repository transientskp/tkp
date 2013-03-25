.. _cuisine:

Cuisine
=======

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
:ref:`transient search <trap:transient-search-recipe>` recipe consists
only of a master recipe: any computational intensive work is actually
done inside the database, and the overhead of starting up a compute
node to interact with the database is probably more than calling the
database directly from the master (front end) node.


A note on database connections: these cannot be transferred from the
master to the node recipes (cannot be pickled, and thus cannot be
transferred across the ssh connection), so each compute node has to
open its own database connection, and close it again. The most obvious
way (if the TKP configuration file is configured correctly) is simply
done on the compute nodes as follows::

    from contextlib import closing
    def run(self, *args):
        with log_time(self.logger):
            with closing(Database()) as database:
	        pass

