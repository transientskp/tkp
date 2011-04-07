# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""This module contains functions that are used to find the best split in a 
set of data (regardless of the splitting method used). Non uniform weights 
of datapoints and more than 2 classes are supported. It is not meant to be
run stand alone."""
from __future__ import division
import math

class EmptyDataSetError(Exception):
    pass

class NegativeWeightsError(Exception):
    pass

def initial_weights(data, n_class):
    """This function calculates the total weight per class and the total 
    Gini score for training sample. This function is called once at the 
    start of tree induction.
    
    arguments:
    data -- a list of tuples or lists with n + 3 entries for data that has 
    n variables. The other three entries, the last and the second to last 
    and the third to last are respectively reserved for the class label and the 
    weight and an unique id (needed during sorting, of which this library does a
    lot). The class labels are integers starting at 0 and going to n_class - 1. 
    n_class -- integer, the number of classes present in the data 
    sample
    
    output:
    total_weight -- sum of the weights of each datapoint in the data
    total_gini -- the gini value of all the data
    """
    if len(data) < 1:
        raise EmptyDataSetError
    
    total_weight = [0 for i in range(n_class)]
    for v in data:
        total_weight[v[-1]] += v[-2]
    
    weight_sum = sum(total_weight)
    
    total_gini = weight_sum * weight_sum
    for j in xrange(n_class):
        total_gini -= total_weight[j] * total_weight[j] 
    total_gini = total_gini / weight_sum

    return total_weight, total_gini


def multi_class_split(data, total_weight, MIN_LEAF_SIZE = 1):
    """This function performs the search for the best split in a given data set
    it should be called with an appropriately sorted list of training data 
    --- be it sorted according to only 1 feature or by projecting all the 
    features on some unit vector for univariate or multivariate splitting. 
    
    arguments:
    data -- a list of tuples or lists with n + 3 entries for data that has 
    n variables. The other three entries, the last and the second to last 
    and the third to last are respectively reserved for the class label and the 
    weight and an unique id (needed during sorting, of which this library does a
    lot). The class labels are integers starting at 0 and going to n_class - 1. 
    total_weight -- float, the total weight of all the datapoints in the data
    argument (passing this to the function avoids having a loop to calculate it)
    MIN_LEAF_SIZE -- integer, the minimum number of datapoints in a leaf node 
    does not take into account the individual weights of the points.
    
    output:
    result_dict -- a dictionary that contains all the interesting values that
    get calculated by this function (like weights after splitting and the gini
    score after splitting). Entries in result_dict:
    "WEIGHT_LEFT" -- key to the sum over all the point weights left of the split
    "WEIGHT_RIGHT" -- key to the sum over all the point weights right of the split 
    "GINI_LEFT" -- key to the gini value left of the split 
    "GINI_RIGHT" -- key to the gini value right of the split
    "GINI" -- key to the sum of the "GINI_LEFT" and "GINI_RIGHT" values
    "SPLIT" -- key to the index that represents the best split in the training data
    """
    
    n_class = len(total_weight)
    weight_right = total_weight[:]
    weight_left = [0 for i in range(n_class)]    
    # larger value than any that can be found after splitting:
    result_dict = {"GINI" : 4 * sum(total_weight)} 
    length = len(data)
    left_sum = sum(weight_left)
    right_sum = sum(weight_right)
    if __debug__:
        tw, tg = initial_weights(data, n_class)
        assert tw == total_weight

    # test all the places that a split can take place
    for i, v in enumerate(data):
        # update the weights left and right of split
        
        weight_left[v[-1]] += v[-2]        
        weight_right[v[-1]] -= v[-2] 
        # I had a problem with weights in these lists becoming negative, that
        # is fixed now (by fixing the sorting).
        # If the problem reoccurs first check wether the total_weight list
        # matches the total_weight that you can calculate using the 
        # initial_weights function. (outside of loop)

        
        left_sum += v[-2]
        right_sum -= v[-2]

        # Check that the split is allowed because of the minimum leaf node size
        # check; if not avoid doing any further calculations for that split:
        if i + 1 >= MIN_LEAF_SIZE and length - i - 1 >= MIN_LEAF_SIZE:
            # sanity checks 
            # (If these fail, code will crash on a zeroDivisionError. Only way
            # to hit these assertions is to input data with weights that are 
            # wrong, negative weights on some points might do the trick.)
            assert left_sum != 0
            assert right_sum != 0
            
            
            left_gini = left_sum * left_sum
            # when i tested it a * a is quicker than a ** 2 (why ?)
            right_gini = right_sum * right_sum
            for j in xrange(n_class):
                left_gini -= weight_left[j] * weight_left[j] 
                right_gini -= weight_right[j] * weight_right[j]
            left_gini = left_gini / left_sum
            right_gini = right_gini / right_sum
            # The above is equivalent to taking the sum over 
            # p_j * p_k for j != k and j, k in [0, 1, ..., n_class -1]
            # under the assumption that:
            # p_0 + p_1 + ... + p_{n_class -1} = 1
            # but faster for problems with more classes in the data. 
            # (The nested loops are doing more multiplications.)

            
            # Check to see wether the split under consideration is actually 
            # better than the ones previously found. At least one such split
            # will be found because this function is only called if 
            # len(data) >= 2 * MIN_LEAF_SIZE and because result_dict["GINI"]
            # is initialized to a large value.
            if left_gini + right_gini < result_dict["GINI"]:
                result_dict = {
                    "WEIGHT_LEFT" : weight_left[:], # list
                    "WEIGHT_RIGHT" : weight_right[:], # list
                    "GINI_LEFT" : left_gini, # float
                    "GINI_RIGHT" : right_gini, # float
                    "GINI" : left_gini + right_gini, # float
                    "SPLIT" : i + 1, # integer
                }
    
    # Some sanity checking, I had a problem with weights becoming negative,
    # that problem is fixed now:
    for X in result_dict["WEIGHT_RIGHT"]:
        if X < 0:
            raise NegativeWeightsError
    for X in result_dict["WEIGHT_LEFT"]:
        if X < 0:
            raise NegativeWeightsError
    return result_dict    

if __name__ == "__main__":
    print __doc__
