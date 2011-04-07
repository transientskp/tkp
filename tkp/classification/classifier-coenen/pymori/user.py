# By Thijs Coenen for Master's research with the Transient Key Project
# december 2007
"""Use the classes and functions in this file to interact with the Pymori 
library."""

from __future__ import division
from util import metadata_container, median_substitute
import tree, pickle


def dump_classifier(filename, c):
    pass

def load_classifier(filename):
    pass

IGNORE_MISSING = 0
MEDIAN_SUBSTITUTION = 1

class __classifier(object):
    """
    This is the base class for the classifiers defined in this module. It 
    implements median substitution for missing data. Objects of this class
    should not be used by themselves. Look at the RF_RI, RF_RC, tree_uni and
    tree_multi classes defined in this module to use the classifiers.
    """
    def run(self, vec, missing_data = IGNORE_MISSING):
        """
        This method wraps the .run method of the various lower level classifier
        objects (as defined in tree.py) and implements median substitution if
        so desired.
        
        input:
        vec -- tuple or list of feature variables of the thing that is to be
        classified (each feature can be either a float or and integer)
        missing_data -- integer, variable that can be used to switch median
        substitution on or off. (Use the IGNORE_MISSING and MEDIAN_SUBSTITUTION
        constants defined in this module as values.)
        
        output:
        a tuple of which the first entry is guaranteed to be the classification,
        the second entry is used to return extra information (number of votes 
        for each class in the case of a random forest and weights for each class
        in the training data in case of a decision tree.)
        
        """
        
        if missing_data == MEDIAN_SUBSTITUTION:
            return self.fc.run(median_substitute(vec, self.md.n_var, 
                self.md.medians))
        else:
            return self.fc.run(vec)

class RF_RI(__classifier):
    """
    Random Forest Classifier, implementing the Random Input selection method.
    """
    def __init__(self, data, n_class, MAX_DEPTH = 5, n_trees = 5, F = 1,
        axis_desc = [], class_desc = []):
        """
        Constructor for this class. If the axis_desc or class_desc variables are
        not of the expected shape or undefined they are set to standard values
        respectively:
        axis_desc = [("x1", ""), ("x2", ""), ..., ("xn", "")] 
        and
        class_desc = ["class 1", "class 2", ..., "class n"]        
        
        input:
        data -- a list of tuples or lists with n + 3 entries for data that has 
        n variables. The other three entries, the last and the second to last 
        and the third to last are respectively reserved for the class label and 
        the weight and an unique id (needed during sorting, of which this 
        library does a lot). The class labels are integers starting at 0 and 
        going to n_class - 1. 
        n_class -- integer, number of classes in the training data
        MAX_DEPTH -- integer, the maximum recursion depth of the decision tree. 
        n_trees -- integer, number of randomized decision trees to add to the 
        random forest classifier
        F -- integer, number of randomly drawn feature variables to consider at 
        each decision node.
        axis_desc -- list. Each entry in the list is a tuple that contains as a 
        first entry the name of the variable and as a second entry the unit that
        it is measured in (also as a string). There should be as many 
        decriptions as there are feature variables.
        class_desc -- list. Each entry in this list is a string that contains 
        the name of the class. There should be as many descriptions as there are
        classes. 
        """
        
        self.md = metadata_container(data, n_class, axis_desc, class_desc)        
        method = {"TRY_FOREST_RI" : True, "F" : F}        
        self.fc = tree.forest_classifier(data,n_class,MAX_DEPTH,n_trees, method)

class RF_RC(__classifier):
    """
    Random Forest Classifier, implementing the Random linear Combinations 
    method.
    """
    def __init__(self, data, n_class, MAX_DEPTH = 5, n_trees = 5, L = 1, F = 1,
        axis_desc = [], class_desc = []):
        """
        input:
        Constructor for this class. If the axis_desc or class_desc variables are
        not of the expected shape or undefined they are set to standard values
        respectively:
        axis_desc = [("x1", ""), ("x2", ""), ..., ("xn", "")] 
        and
        class_desc = ["class 1", "class 2", ..., "class n"]
        
        input
        data -- a list of tuples or lists with n + 3 entries for data that has 
        n variables. The other three entries, the last and the second to last 
        and the third to last are respectively reserved for the class label and 
        the weight and an unique id (needed during sorting, of which this 
        library does a lot). The class labels are integers starting at 0 and 
        going to n_class - 1. 
        n_class -- integer, number of classes in the training data
        MAX_DEPTH -- integer, the maximum recursion depth of the decision tree. 
        n_trees -- integer, number of randomized decision trees to add to the 
        random forest classifier
        L -- integer, number of feature variables that need to be combined into
        a random linear combination
        F -- integer, number of trials to perform for each decision node
        axis_desc -- list. Each entry in the list is a tuple that contains as a 
        first entry the name of the variable and as a second entry the unit that
        it is measured in (also as a string). There should be as many 
        decriptions as there are feature variables.
        class_desc -- list. Each entry in this list is a string that contains 
        the name of the class. There should be as many descriptions as there are
        classes.         
        """
        
        self.md = metadata_container(data, n_class, axis_desc, class_desc)
        method = {"TRY_FOREST_RC" : True, "F" : F, "L" : L}        
        self.fc = tree.forest_classifier(data,n_class,MAX_DEPTH,n_trees, method)

class tree_uni(__classifier):
    """
    Decision tree classifier implementing univariate splitting.
    """
    def __init__(self, data, n_class, MIN_LEAF_SIZE = 1, MAX_DEPTH = 5, 
        axis_desc = [], class_desc = []):
        """
        input:
        Constructor for this class. If the axis_desc or class_desc variables are
        not of the expected shape or undefined they are set to standard values
        respectively:
        axis_desc = [("x1", ""), ("x2", ""), ..., ("xn", "")] 
        and
        class_desc = ["class 1", "class 2", ..., "class n"]
        
        input
        data -- a list of tuples or lists with n + 3 entries for data that has 
        n variables. The other three entries, the last and the second to last 
        and the third to last are respectively reserved for the class label and 
        the weight and an unique id (needed during sorting, of which this 
        library does a lot). The class labels are integers starting at 0 and 
        going to n_class - 1. 
        n_class -- integer, number of classes in the training data
        MIN_LEAF_SIZE -- integer, minimum leaf node size for the decision tree 
        that is constructed by this function. Trees with too small leaf node 
        sizes generalize badly to new data.
        MAX_DEPTH -- integer, the maximum recursion depth of the decision tree. 
        axis_desc -- list. Each entry in the list is a tuple that contains as a 
        first entry the name of the variable and as a second entry the unit that
        it is measured in (also as a string). There should be as many 
        decriptions as there are feature variables.
        class_desc -- list. Each entry in this list is a string that contains 
        the name of the class. There should be as many descriptions as there are
        classes.         
        """

                
        self.md = metadata_container(data, n_class, axis_desc, class_desc)
        method = {"TRY_UNIIVARIATE" : True}
        self.fc = tree.tree_classifier(data, n_class, MAX_DEPTH, MIN_LEAF_SIZE,
            method)

class tree_multi(__classifier):
    """
    Decision tree classifier implementing univariate splitting.    
    """
    def __init__(self, data, n_class, MIN_LEAF_SIZE = 1, MAX_DEPTH = 5, 
        axis_desc = [], class_desc = []):
        """
        input:
        Constructor for this class. If the axis_desc or class_desc variables are
        not of the expected shape or undefined they are set to standard values
        respectively:
        axis_desc = [("x1", ""), ("x2", ""), ..., ("xn", "")] 
        and
        class_desc = ["class 1", "class 2", ..., "class n"]
        
        input
        data -- a list of tuples or lists with n + 3 entries for data that has 
        n variables. The other three entries, the last and the second to last 
        and the third to last are respectively reserved for the class label and 
        the weight and an unique id (needed during sorting, of which this 
        library does a lot). The class labels are integers starting at 0 and 
        going to n_class - 1. 
        n_class -- integer, number of classes in the training data
        MIN_LEAF_SIZE -- integer, minimum leaf node size for the decision tree 
        that is constructed by this function. Trees with too small leaf node 
        sizes generalize badly to new data.
        MAX_DEPTH -- integer, the maximum recursion depth of the decision tree. 
        axis_desc -- list. Each entry in the list is a tuple that contains as a 
        first entry the name of the variable and as a second entry the unit that
        it is measured in (also as a string). There should be as many 
        decriptions as there are feature variables.
        class_desc -- list. Each entry in this list is a string that contains 
        the name of the class. There should be as many descriptions as there are
        classes.         
        """
                
        self.md = metadata_container(data, n_class, axis_desc, class_desc)
        method = {"TRY_UNIVARIATE" : True, "TRY_MULTIVARIATE" : True}
        self.fc = tree.tree_classifier(data, n_class, MAX_DEPTH, MIN_LEAF_SIZE,
            method)

if __name__ == "__main__":
    print __doc__