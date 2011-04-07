# By Thijs Coenen for master's research with the Transient Key Project
from __future__ import division
import random, math
# Coordinate scaler for clustering algorithms + clusterig algorithms ...
# Coded with no concern for speed whatsoever!
# Uses the same "shape" of data as the tree algorithms.

def to_bbox(data):
    n_var = len(data[0]) - 3
    bbox = [(data[0][i], data[0][i]) for i in xrange(n_var)]
    for v in data:
        for i in xrange(n_var):
            if v[i] < bbox[i][0]:
                bbox[i] = (v[i], bbox[i][1])
            if v[i] > bbox[i][1]:
                bbox[i] = (bbox[i][0], v[i])
    return bbox
            
def normalize(data):
    normalized = []
    bbox = to_bbox(data)
    n_var = len(data[0]) - 3
    for v in data:
        new_v = [v[i] - bbox[i][0] / (bbox[i][1] - bbox[i][0]) for i in xrange(n_var)]
        new_v.extend([v[-3], v[-2], v[-1]])
        normalized.append(tuple(new_v))
    return normalized

def k_means(data, k, MAX_RUNS = 100):
    n_var = len(data[0]) - 3
    bbox = to_bbox(data)
    centers = [[random.random() * (bbox[i][1] - bbox[i][0]) + bbox[i][0] for i in xrange(n_var)] for ii in xrange(k)]
    members = []
    
    MAX_DIST = math.sqrt(sum([(bbox[i][1] - bbox[i][0]) ** 2 for i in xrange(n_var)]))
    
    def dist(v1, v2):
        return math.sqrt(sum([(v1[i] - v2[i]) ** 2 for i in xrange(n_var)]))

    ir = 0
    while ir < MAX_RUNS:
        for v in data:
            # update cluster membership:
            d = MAX_DIST
            cluster_idx = -1
            for i in xrange(k):
                new_d = dist(centers[i], v)
                if new_d < d:
                    cluster_idx = i
                    d = new_d
            members.append(cluster_idx)
            # now update cluster centers:
            new_centers = [[0 for i in xrange(n_var)] for ii in xrange(k)]
            new_numbers = [0 for i in xrange(k)]

        for i, v in enumerate(data):
            new_numbers[members[i]] += 1
            for ii in xrange(n_var):
                new_centers[members[i]][ii] += v[ii]

        for i in xrange(k):
            # Warning my implementation does not remove an empty cluster, it 
            # just draws a new random vector (this might not be the correct
            # way to deal with empty clusters --- might well srew up some 
            # convergence criteria).
            if new_numbers[i] != 0:
                for ii in xrange(n_var):
                    new_centers[i][ii] /= new_numbers[i]
            else:
                new_centers[i][ii] = random.random() * (bbox[ii][1] - bbox[ii][0]) + bbox[ii][0]
                
        print new_centers
        ir += 1
        members = []
        
        if new_centers == centers:
            break
        centers = new_centers
    return centers
    
def SOM1d(data, k):
    pass

if __name__ == "__main__":
    data = [(random.random(), random.random(), i, 1, 0) for i in range(100)]
    data.extend([(random.random() + 10, random.random() + 10, i + 100, 1, 0) for i in range(100)])
    k_means(data, 10, 1000)
    