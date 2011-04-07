# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""This module contains functions to find multivariate splits (splits based
on linear combinations of features). This is not meant to be run stand alone."""
# XXX clean up ongoing, I want all the vectors in this module to have:
# len(vector) == n_dim 

from __future__ import division
import math, random
from core import multi_class_split

def inner(v1, v2, mask):
    """Inner product, features can be masked out.
    
    input:
    v1 and v2 -- lists or tuples representing vectors. It is no problem if they
    still have weights and class labels attached to them, just use mask to
    mask them out.
    n_dim -- integer, number of variables in the vectors that are not class
    labels or weights
    mask -- list of integers that are the indexes of the variables in the 
    data to take into account whilst calculating the inner product.
    
    output:
    tmp -- float or integer that is the inner product of v1 with v2 only taking
    into account the features listed in mask.
    """
    tmp = 0
    for i in mask:
        tmp += v1[i] * v2[i]
    return tmp # seems ok
    
def average(unit_vectors, n_dim, mask):
    """Takes the average of a set of unit vectors, returns a unit vector.
    
    input:
    unit_vectors -- list of vectors where each vector is a list or a tuple
    of floats (or integers). The unit vectors should have n_dim entries, 
    if they have more they will be silently ignored (so weights and class
    labels are ignored)
    n_dim -- integer, number of variables in the unit_vectors (data). Note
    that this number need not match the number of entries in the mask.
    mask -- list of indices of variables in the unit vectors to consider
    
    output:
    out -- a unit_vector that is the 'average' of the input unit_vectors
    (only thos components specified in mask)
    """
    out = [0 for i in xrange(n_dim)]
    for i in mask:
        out[i] += sum([v[i] for v in unit_vectors])
    norm = 1 / math.sqrt(sum([out[i] * out[i] for i in mask])) 
    for i in mask:
        out[i] *= norm
    return out # seems ok
    
def mirror(vec1, vec2, n_dim, mask):
    """Takes two unit vectors vec1 and vec2 and 'mirrors' vec1 around vec2.
    This takes place on a unit sphere of dimension len(mask).
    
    input:
    vec1 -- list of floats, representing a unit vector
    vec1 -- list of floats, representing a unit vector    
    n_dim -- integer, number of variables in the unit_vectors (data). Note
    that this number need not match the number of entries in the mask.
    mask -- list of indices of variables in the unit vectors to consider

    output:
    this function returns a vector that is unit vector vec1 mirrored around
    unit vector vec2 (only those components specified in the mask)
    """
    cos_alpha = sum([vec1[i] * vec2[i] for i in mask])
    delta = [0 for i in xrange(n_dim)]
    for i in mask:
        delta[i] = cos_alpha * vec2[i] - vec1[i]
    return [vec1[i] + 2 * delta[i] for i in mask] # seems ok

def create_simplex_random(n_dim, mask):
    """Creates a simplex on a unit sphere of dimension len(mask), this 
    means that the simplex also has len(mask) points. 
    
    input:
    n_dim -- integer, number of variables in the unit_vectors (data). Note
    that this number need not match the number of entries in the mask.
    mask -- list of indices of variables in the data to consider

    output:
    simplex -- a list of unit vectors that represent a simplex on a unit 
    sphere in n dimensions where n = len(mask). This simplex has n entries
    because the surface of the sphere has n - 1 dimensionality.
    """
    simplex = []
    for i in mask:
        u = [0 for ii in range(n_dim)]
        for ii in mask:
            u[ii] = random.random()
        norm = 1 / math.sqrt(sum([u[ii] * u[ii] for ii in mask])) 
        for ii in mask:
            u[ii] *= norm
        assert len(u) == n_dim
        simplex.append(u)
    return simplex

def simplex_on_sphere(data, total_weight, n_dim, mask, MIN_LEAF_SIZE):
    """This function looks for a multivariate split, some of the features
    can be dropped from consideration by masking them out. The method used
    to look for the best split is inspired by the downhill simplex method
    of function minimization. I am looking for the best unit vector to 
    project all the data on. The simplex is made up of several unitvectors
    that are constrained to to walk across the surface of a (hyper)sphere.
    
    input:
    data -- a list of tuples or lists with n + 3 entries for data that has 
    n variables. The other three entries, the last and the second to last 
    and the third to last are respectively reserved for the class label and the 
    weight and an unique id (needed during sorting, of which this library does a
    lot). The class labels are integers starting at 0 and going to n_class - 1. 
    total_weight -- list of floats (or integers), the total weight of all the 
    datapoints in the data (one entry for each class, indexed by class label).
    Passing this to the function avoids having a loop to recalculate it.
    mask -- a list of integers that are the indices of the feature that should
    be considered.
    MIN_LEAF_SIZE -- integer, the minimum number of datapoints in a leaf node 
    does not take into account the individual weights of the points.
    
    output:
    best_result -- a dictionary containing all the relevant data about the 
    split generated by this function. The keys of this dictionary are those
    that were returned by the core.multi_class_split function and a few new 
    ones:
    "VECTOR" : the normal of the hyper plane that splits the data
    "TYPE" : the type of split, "MULTIVARIATE" in this case
    "SPLIT_AT_VALUE" : the distance that the hyperplane that splits the 
    data is away from the origin (the hyper plane's normal is represented
    by best_result["VECTOR"]
    "MASK" : list of indices of the variables used in the split

    """
    MAX_RUNS = 100
    assert n_dim > 1
    
    def score(u):
        data.sort(key = lambda x : inner(u, x, mask))
        r = multi_class_split(data, total_weight, MIN_LEAF_SIZE)
        return r
    
    simplex = create_simplex_random(n_dim, mask)
    scored_simplex = []
    for u in simplex:
        r = score(u) 
        scored_simplex.append((r["GINI"], r, u))
    scored_simplex.sort()
    
    hlp1, hlp2, hlp3 = 0, 0, 0
    
    for i in range(MAX_RUNS):
        worst = scored_simplex.pop(-1)
        centroid = average([v[2] for v in scored_simplex], n_dim, mask) # not taking the worst one into account
        
        first_try = mirror(worst[2], centroid, n_dim, mask)
        first_try_r = score(first_try)
        hlp1 = first_try_r["GINI"]
        if first_try_r["GINI"] < scored_simplex[0][0]:
            second_try = mirror(centroid, first_try, n_dim, mask)
            second_try_r = score(second_try)
            if second_try_r["GINI"] < first_try_r["GINI"]:
                scored_simplex.append((second_try_r["GINI"], second_try_r, second_try))
            else:
                scored_simplex.append((first_try_r["GINI"], first_try_r, first_try))
        else:
            second_try = average([centroid, worst[2]], n_dim, mask)
            second_try_r = score(second_try)
            hlp2 = second_try_r["GINI"]
            if second_try_r["GINI"] < scored_simplex[0][0]:
                scored_simplex.append((second_try_r["GINI"], second_try_r, second_try))
            else:
                # waardeloos, dan maar krimpen in de hoop wat te vinden :)
                scored_simplex.append(worst)
                for ii in range(1, len(scored_simplex)): # replace len(scored_simplex) with n_dim
                    new_v = average([scored_simplex[0][2], scored_simplex[ii][2]], n_dim, mask)
                    new_v_r = score(new_v)
                    hlp3 = new_v_r["GINI"]
                    scored_simplex[ii] = (new_v_r["GINI"], new_v_r, new_v)
        scored_simplex.sort()
        # convergence criterion of sorts
        if hlp1 == hlp2 == hlp3:
            break        

    best_result = scored_simplex[0][1]
    best_result["VECTOR"] = scored_simplex[0][2]
    slice = best_result["SPLIT"]
    left_of_split = inner(scored_simplex[0][2], data[slice - 1], mask)
    right_of_split = inner(scored_simplex[0][2], data[slice], mask)
    best_result["SPLIT_AT_VALUE"] = 0.5 * (left_of_split + right_of_split)
    best_result["TYPE"] = "MULTIVARIATE"
    best_result["MASK"] = mask
    return best_result
    
def multivariate_split(data, total_weight, MIN_LEAF_SIZE):
    """Wrapper function that calls the simplex_on_sphere function to look
    for a multivariate split. This function calculates the appropriate mask
    for taking into account all the different features in the data.
    
    data -- a list of tuples or lists with n + 3 entries for data that has 
    n variables. The other three entries, the last and the second to last 
    and the third to last are respectively reserved for the class label and the 
    weight and an unique id (needed during sorting, of which this library does a
    lot). The class labels are integers starting at 0 and going to n_class - 1. 
    total_weight -- list of floats (or integers), the total weight of all the 
    datapoints in the data (one entry for each class, indexed by class label).
    
    output:
    result_dict -- a dictionary containing all the relevant data about the 
    split generated by this function. The keys of this dictionary are those
    that were returned by the core.multi_class_split function and a few new 
    ones:
    "VECTOR" : the normal of the hyper plane that splits the data
    "TYPE" : the type of split, "MULTIVARIATE" in this case
    "SPLIT_AT_VALUE" : the distance that the hyperplane that splits the 
    data is away from the origin (the hyper plane's normal is represented
    by result_dict["VECTOR"]
    "MASK" : list of indices of the variables used in the split
    
    """ 
    n_dim = len(data[0]) - 3
    mask = range(n_dim)
    result_dict = simplex_on_sphere(data, total_weight, n_dim, mask, MIN_LEAF_SIZE)
    return result_dict
    
def forest_RC(data, total_weight, MIN_LEAF_SIZE, L, F):
    """This function is used to build trees that have splits based on random
    linear combinations of features"""
    assert F > 0
    
    tmp_mask = range(len(data[0]) - 3)
    result_dict = {"GINI" : 3 * sum(total_weight)}

    for i in xrange(F):
        random.shuffle(tmp_mask)
        mask = tmp_mask[0:L]
        coefficients = [0 for i in xrange(len(data[0]))]

        for i in mask:
            coefficients[i] = 2 * random.random() - 1 

        data.sort(key = lambda x : (inner(coefficients, x, mask), x[-3]))
        r = multi_class_split(data, total_weight, MIN_LEAF_SIZE)

        if r["GINI"] < result_dict["GINI"]:
            result_dict = r
            result_dict["VECTOR"] = coefficients
            result_dict["MASK"] = mask
            result_dict["TYPE"] = "MULTIVARIATE"
            slice = result_dict["SPLIT"]
            left_of_split = inner(result_dict["VECTOR"], data[slice - 1], mask)
            right_of_split = inner(result_dict["VECTOR"], data[slice], mask)
            result_dict["SPLIT_AT_VALUE"] = 0.5 * (left_of_split + right_of_split)
    assert "SPLIT_AT_VALUE" in result_dict
        
    return result_dict


if __name__ == "__main__":
    print __doc__