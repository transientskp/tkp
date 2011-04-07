from __future__ import division
# this file contains the parts of the tree inducing algorithm that are used to
# judge the quality of univariate splits 

def signal_to_noise(data):
    """For use in 2 class classification problem, singnal vectors are assumed
    to be labeled 1, noise vectors labeled with 0. All weights taken to be 
    equal."""
    n_signal = 0
    for v in data:
        n_signal += v[-1]
    return n_signal / len(data)

def find_split(data, MIN_LEAF_SIZE):
    """Expects only sorted data, data is a list of tuples where the last entry
    in the tuple is the classification. This function furthermore assumes a 
    two class problem, SIGNAL = 1 and NOISE = 0 ."""
    # idea to speed this up : use enumerate() for the loop
    length = len(data)
    total_signal = 0
    for v in data:
        total_signal += v[-1]
    last_left_signal = 0
    best_gini = length # guaranteed to be larger than any calculated gini
    split_after_index = 0 # not interesting now
    
    for i in xrange(1, length):
        left_signal = last_left_signal + data[i - 1][-1]
        right_signal = total_signal - left_signal
        l_size = i
        r_size = (length - i)
        pl = left_signal / l_size
        pr = right_signal / r_size
        gini = pl * (1 - pl) * l_size +  pr * (1 - pr) * r_size
        if gini < best_gini and r_size >= MIN_LEAF_SIZE and l_size >= MIN_LEAF_SIZE:
            split_after_index = i - 1
            best_gini = gini
        last_left_signal = left_signal
    return best_gini, split_after_index
