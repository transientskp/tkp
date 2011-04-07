"""
This module contains a function check_input that can be used to check wether,
training / validation data matches what the tree inducers are expecting.
"""

def check_input(data):
    # returns True if ok
    classes = {}
    indices = {}
    n_var = len(data[0]) - 3
    if n_var < 2: # at least 2 for random forests
        print "Fewer than 2 variables, makes no sense when used with random forests"
        return False
    for v in data:
        if len(v) - 3 != n_var:
            print "Not all example vectors have the same length."
            return False
        if v[-2] <= 0:
            print "Negative or zero weight for vector."
            return False
        if type(v[-1]) != type(1):
            print "Class label not integer, i.e. wrong!"
            return False
        try:
            classes[v[-1]] += 1
        except KeyError:
            classes[v[-1]] = 1
        if indices.has_key(v[-3]):
            print "No unique ids on example vectors"
            return False
        else:
            indices[v[-3]] = 1
    k = classes.keys()
    k.sort()
    if not k[0] == 0:
        print "Class labels don't include 0"
        return False
    for i in range(1, len(k)):
        if k[i] - k[i - 1] != 1:
            print "Class labels are not consequtive integers, i.e. wrong!"
            return False
    
    print "Input data should be ok."
    return True

if __name__ == "__main__":
    print __doc__
