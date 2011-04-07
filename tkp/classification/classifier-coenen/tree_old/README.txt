This directory contains a decision tree inducer that can use univariate and 
multivariate splitting criteria. Look at test.py for some of the ways to run it.

The xml handling depends on the ElementTree package that is standard in 
python2.5 but can be installed for older versions of python. The plotting is 
done using pylab, but pylab and numpy are not used in the tree induction.


tree_builder.py contains the tree induction algorithm
multivariate.py multivariate splitting needed by tree_builder.py
univariate.py univariate splitting needed by tree_builder.py and multivariate.py
test.py messy testing code (builds a tree, makes plots etc.)
tree_reader.py takes an xml representation of decision tree then builds a classifier
dataset.py 'fake' data for testing purposes

stuff that you might come across after a run:
nodes.xml xml representation of a decision tree
nodes.dot dot file for use with Graphiz plotting package (plots tree structure
    not the actual decisions)
node1.png plot of the contents of a node (whole set for root node of decision
    tree, progressively smaller sets for nodes deeper in the tree). The 1 could
    be any number (but the numbers of the png files correspond to the numbers 
    in the dot file).
    
.pyc files ('compiled' python bytecode files)

