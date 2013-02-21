This directory contains various recipes to be used in the TRAnsient Pipeline (TRAP).

The recipes are categorised into four subdirectories:

* master/ contains the recipes to be run on the front-end node

* nodes/ contains the recipes to be run on the compute nodes; these
  are accompanied by a recipe in master/

* distributed/ contains copies of the recipes in master/ that run distributed.

* standalone/ contains recipes that run standalone, ie, non-distributed. 

One would have to copy the correct recipe from standalone or
distributed into the master directory to have that recipe run only on
the front-end or distributed, respectively. Not all recipes can be run
distributed; these will only be found in standalone.


Recipes
-------

- trap.py: main recipe, that runs the other recipes.

- DBase: connects to the database, and returns a database connection
  object. This connection objects is passed around in trap.py to other
  recipes(*).

- SourceAssociation: runs the database source association algorithm on
  the newly inserted sources.

- TransientSearch: find transients, by calculating the chi^2 value of
  their light curve. Returns a set of transients ids.

- FeatureExtraction: extract useful characteristics from identified
  transients. Returns transients objects with corresponding
  characteristics.

- Classification: classify transients. Assign weights for possible
  source classifications to the transients objects.

(*) A database object can't be passed from the front end node to a
compute node; the compute nodes will need to create their own database
connection separately.


Documentation
-------------

Full documentation is available in Restructred Text format in the
docs/source subdirectory.
