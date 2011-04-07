from __future__ import division
from random import randrange

def winner(scores):
    """Finds the best classifiacation from a list of votes or weights, assuming
    that large numbers are better. In case there is a tie, this function chooses
    a classification at random (from the tied best cases)."""
    best = scores[0]
    idx = [0]
    for i in range(1, len(scores)):
        if scores[i] == best:
            idx.append(i)
        elif scores[i] > best:
            best = scores[i]
            idx = [i]
    return idx[randrange(len(idx))]

def margin(scores):
    """Calculates the margin from a set of scores."""
    if scores[0] > scores[1]:
        best = scores[0]
        second_best = scores[1]
    else:
        best = scores[1]
        second_best = scores[0]
    for i in xrange(2, len(scores)):
        if scores[i] > best:
            second_best, best = best, scores[i]
        elif scores[i] > second_best:
            second_best = scores[i]
    return best - second_best


class metadata_container(object):
    def __init__(self, data, n_class, axis_desc, class_desc):
        self.n_var = len(data[0]) - 3
        self.n_class = n_class
        self.bbox = bbox(data)
        self.medians = medians(data)
        self.class_dist = class_dist(data)
        if ok_axis_labelling(axis_desc, self.n_var):
            self.axis_desc = axis_desc
        else:
            self.axis_desc = [("x" + str(i), "") for i in xrange(self.n_var)]
        if ok_class_labelling(class_desc, self.n_class):
            self.class_desc = class_desc
        else:
            self.class_desc = ["class " + str(i) for i in xrange(n_class)]

def bbox(data):
    n_examples = len(data)
    n_var = len(data[0]) - 3
    bbox = [(data[0][i], data[0][i]) for i in xrange(n_var)]
    for v in data:
        for i in xrange(n_var):
            if v[i] < bbox[i][0]:
                bbox[i] = (v[i], bbox[i][1])
            elif v[i] > bbox[i][1]:
                bbox[i] = (bbox[i][0], v[i])
    return bbox
    
def medians(data):
    n_examples = len(data)
    n_var = len(data[0]) - 3
    medians = []
    # There is a O(n) way of calculating medians, this is not it.
    for i in xrange(n_var):
        data.sort(key = lambda x : x[i])
        if n_examples % 2 == 0:
            median = (data[int(n_examples / 2)][i] + 
                data[int(n_examples / 2) + 1][i]) / 2
            medians.append(median)
        else:
            median = data[n_examples // 2][i]
            medians.append(median)
    return medians

def class_dist(data):
    class_dict = {}
    for v in data:
        try:
            class_dict[v[-1]] += 1
        except KeyError:
            class_dict[v[-1]] = 1
    keys = class_dict.keys()
    keys.sort()
    return [class_dict[k] for k in keys]

def median_substitute(vec, n_var, medians):
    nv = []
    for i in xrange(n_var):
        if vec[i] == None and i < n_var: nv.append(medians[i])
        else: nv.append(vec[i])
    for i in xrange(n_var, len(vec)):
        nv.append(vec[i])
    return nv

def ok_axis_labelling(axis_desc, n_var):
    if type(axis_desc) != type([]) or  type(n_var) != type(1):
        return False
    if len(axis_desc) != n_var: 
        return False
    for X in axis_desc:
        if len(X) != 2: 
            return False
        elif type(X[0]) != type("") or type(X[1]) != type(""):
            return False
    return True

def ok_class_labelling(class_desc, n_class):
    if len(class_desc) != n_class:
        return False
    for x in class_desc:
        if type(x) != type(""): return False
    return True

