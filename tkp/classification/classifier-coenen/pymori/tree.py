# By Thijs Coenen oktober - december 2007 for Research with the Transient Key 
# Project
"""This module contains the function that builds a decision tree classifier
and 2 classes tree_classifier and forest_classifier. This module is not meant
to be run stand alone."""

from __future__ import division
from univariate import univariate_split, forest_RI
from multivariate import multivariate_split, forest_RC, inner
import math, random
from core import initial_weights
from util import winner

def build_tree(data, total_weight, total_gini, depth, MIN_LEAF_SIZE, MAX_DEPTH, 
    method):
    """This function builds a decision tree, in the process it calls itself 
    recursively untill no further splits can be made in the data set.
    
    input:
    data -- a list of tuples or lists with n + 3 entries for data that has 
    n variables. The other three entries, the last and the second to last 
    and the third to last are respectively reserved for the class label and the 
    weight and an unique id (needed during sorting, of which this library does a
    lot). The class labels are integers starting at 0 and going to n_class - 1. 
    total_weight -- sum of the weights of each datapoint in the data
    total_gini -- the gini value of all the data
    MIN_LEAF_SIZE -- integer, minimum leaf node size for the decision tree 
    that is constructed by this function. Trees with too small leaf node sizes 
    generalize badly to new data.
    MAX_DEPTH -- integer, the maximum recursion depth of the decision tree. 
    method -- a dictionary that holds all the needed parameters that are 
    specific to the method used to construct the tree
    
    output:
    nl -- a leaf node or a whole decision tree represented as linked 
    dictionaries, this output must be wrapped by a tree_classifier object
    to construct a 'life' decision tree.
    
    """

    for x in total_weight:
        assert x >= 0
    
    assert type(data) == type([])
    assert len(data) > 0
    n_dim = len(data[0]) - 3 # number of variables in the data
    n_class = len(total_weight) # number of classes
    
    # Check some of the conditions that stop creation of new nodes since these 
    # checks are 'cheap' compared to trying to split nodes I perform them first:
    CONTINUE = True
    if depth >= MAX_DEPTH:
        CONTINUE = False # Maximum recursion depth reached, creating leaf
    elif len(data) < 2 * MIN_LEAF_SIZE:
        CONTINUE = False # 2 times minimum leaf size reached, creating leaf
    else:
        for x in total_weight:
            if x == sum(total_weight):
                CONTINUE = False # Pure node found, creating leaf
            else:
                pass # Non pure node, continuing

    # Try the different methods of splitting nodes specified in the method list,
    # but only if none of the above checks forced a stop to the recursion.
    if CONTINUE:
        results = []
        if method.has_key("TRY_UNIVARIATE"):
            results.append(univariate_split(data, total_weight, MIN_LEAF_SIZE))
        if method.has_key("TRY_MULTIVARIATE"):
            results.append(multivariate_split(data, total_weight,MIN_LEAF_SIZE))
        if method.has_key("TRY_FOREST_RI"):
            results.append(forest_RI(data, total_weight, MIN_LEAF_SIZE,
            method["F"]))
        if method.has_key("TRY_FOREST_RC"):
            results.append(forest_RC(data, total_weight, MIN_LEAF_SIZE, 
            method["L"], method["F"]))
            
        
        results = [(r["GINI"], r) for r in results]
        results.sort()

        if len(results) > 0:
            best_split = results[0][1]
            if best_split["GINI"] < total_gini:
                # Note that best_split["GINI"] is the sum of the gini values
                # calculated for the left and right branches of best_split and
                # that total_gini is the gini value before that split is 
                # performed, likewise total_weight is the weight before the 
                # split best_split is performed.
                node = best_split 
                # The nodes in the decision tree are represented by dictionaries
                # that hold all the data relevant to each split.
                node["TOTAL_WEIGHT"] = total_weight
                node["TOTAL_GINI"] = total_gini
                slice = best_split["SPLIT"]

                # Sort the data in a way that is appropriate to the type of 
                # split found:
                if node["TYPE"] == "UNIVARIATE":
                    # This is used by univariate splitting and by forest_RI 
                    data.sort(key = lambda x: (x[best_split["AXIS"]], x[-3]))
                    
                elif best_split["TYPE"] == "MULTIVARIATE":
                    # This is used by multivariate splitting and forest_RC
                    u = best_split["VECTOR"]
                    mask = best_split["MASK"]
                    data.sort(key = lambda x: (inner(x, u, mask), x[-3]))
                
                # Recursively create the left and right branches:
                node["LEFT"] = build_tree(data[0:slice], 
                    best_split["WEIGHT_LEFT"], best_split["GINI_LEFT"], 
                    depth + 1, MIN_LEAF_SIZE, MAX_DEPTH, method)
                node["RIGHT"] =  build_tree(data[slice:len(data)], 
                    best_split["WEIGHT_RIGHT"], best_split["GINI_RIGHT"], 
                    depth + 1, MIN_LEAF_SIZE, MAX_DEPTH, method)
                
                # Delete all the keys from the dictionary that are not needed to
                # represent the decision in the decision tree:
                for k in ["GINI_LEFT", "GINI_RIGHT", "WEIGHT_LEFT", 
                    "WEIGHT_RIGHT", "GINI", "SPLIT"]:
                    del node[k]
                return node # Return the decision node
            else:
                pass # Tried splitting, found no split that was good enough, 
                     # returning leaf

    # No suitable split was found, or the recursision was forced to stop, a
    # leaf node should be returned:
    nl = {}
    nl["TOTAL_WEIGHT"] = total_weight
    nl["TOTAL_GINI"] = total_gini
    nl["TYPE"] = "LEAF"
    return nl

class tree_classifier(object):
    """Class that wraps a decision tree constructed by the build_tree function.
    To use the tree_classifier.run function."""
    def __init__(self, data, n_class, MAX_DEPTH, MIN_LEAF_SIZE, method):
        iw, ig = initial_weights(data, n_class)
        root_node = build_tree(data, iw, ig, 0, MIN_LEAF_SIZE,MAX_DEPTH, method)
        self.tree = root_node
        
    def check(self, node, v):
        """This function checks which of the branches in the decision tree
        the vector v must go down given the decision at node, it then 
        recursively calls itself using the left or right child node of the node
        currently under consideration. At a leaf the total weight is returned
        which can then be used to calculate the most likely class.
        This function is internal to the tree classifier and should not be 
        called from the outside use the tree_classifier.run function instead. 
        
        input:
        node -- the decision node (represented as a dictionary) in the 
        decision tree to check
        v -- the vector (list or tuple) that needs to be classified.
        
        output:
        list of the weights for each of the classes in the learning sample (this
        is the output after the recursion has finished).
        """
        if node["TYPE"] == "UNIVARIATE":
            if v[node["AXIS"]] < node["SPLIT_AT_VALUE"]:
                return self.check(node["LEFT"], v)
            else:
                return self.check(node["RIGHT"], v)
        elif node["TYPE"] == "MULTIVARIATE":
            tmp = inner(v, node["VECTOR"], node["MASK"])
            if tmp < node["SPLIT_AT_VALUE"]:
                return self.check(node["LEFT"], v)
            else:
                return self.check(node["RIGHT"], v)
        elif node["TYPE"] == "LEAF":
            return node["TOTAL_WEIGHT"]
        else:
            print "NODE OF UNKNOWN TYPE ENCOUNTERED"
            assert False # this should not happen!
    
    def run(self, v):
        """This is the function to run to perform the classification. The 
        first entry of the output tuple is the most probable classification
        according to the tree_classifier.
        
        input:
        v -- a vector (list or tuple) of the data to be classified, a.k.a. 
        a feature vector.
        
        output:
        tuple with as first entry the most probable classification, and as
        second entry a list of the weights per class in the leaf node that
        lead to the classification.
        """
    
        w = self.check(self.tree, v)
        return winner(w), w

class forest_classifier(object):
    """This class is wraps several tree classifiers objects to form a forest
    of classifiers. The random forest algorithms need this class. 
    An Out-of-bag error estimate is also calculated."""
    def __init__(self, data, n_class, MAX_DEPTH, n_trees, method):
        self.forest = []
        self.n_class = n_class
        split_idx = int(len(data) * (1 - 1 / math.e))
        
        oob_vote = [[0 for ii in xrange(n_class)] for i in xrange(len(data))]
        idx_map = {}
        for i, v in enumerate(data):
            idx_map[v[-3]] = i
        
        for i in xrange(n_trees):
            random.shuffle(data)
            t_data = data[0: split_idx]
            oob_data = data[split_idx: len(data)]
            tc = tree_classifier(t_data, n_class, MAX_DEPTH, 1, method)
            for v in oob_data:
                oob_vote[ idx_map[v[-3]] ][tc.run(v)[0]] += 1
            self.forest.append(tc)

        ok = 0
        for v in data:
            tmp = oob_vote[idx_map[v[-3]]].index(max(oob_vote[idx_map[v[-3]]]))
            if v[-1] == tmp:
                ok += 1
        self.oob_error_estimate = 1 - ok / len(data)
        
    def run(self, v):
        """This function performs the classification using all the 
        decision trees in the forest. 
        
        input:
        v -- a vector (list or tuple) of the data to be classified, a.k.a. 
        a feature vector.
        
        output:
        A tuple with as first entry the classification, the second entry is a 
        list of votes for the classes. This list has as many entries as there 
        were classes in the training data. For instance, for n classes:
        [<votes for class 0>, <votes for class 1>, ..., <votes for class n>]
        The sum total of the votes in this list matches the number of decision
        trees in the forest.
        """
        assert len(self.forest) > 0
        outcome = []
        scores = [0 for i in xrange(self.n_class)]
        for tc in self.forest:
            assert isinstance(tc, tree_classifier)
            vote, weights = tc.run(v)
            scores[vote] += 1
        return winner(scores), scores
        
if __name__ == "__main__":
    print __doc__

