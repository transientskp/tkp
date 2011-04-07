from __future__ import division
import math
from univariate import find_split

def inner(vec1, vec2):
    n_dim = len(vec1)
    return sum([vec1[i] * vec2[i] for i in xrange(n_dim)])

def average(l):
    """takes the average of a set of vectors"""
    n_dim = len(l[0])
    out = []
    for i in range(n_dim):
        sum_i = 0
        for ii in range(len(l)):
            sum_i += l[ii][i]
        out.append(sum_i)
    for i in xrange(n_dim):
        out[i] = out[i] / len(l)
    return out

def mirror(vec1, vec2):
    """ mirrors vec1 around vec2 , assumes normalized vectors"""
    n_dim = len(vec1)
    cos_alpha = inner(vec1, vec2)
    delta = [cos_alpha * vec2[i] - vec1[i] for i in xrange(n_dim)]
    mirrored = [vec1[i] + 2 * delta[i] for i in xrange(n_dim)]
    return mirrored
    
def normalize(vec):
    N = 1 / math.sqrt(inner(vec, vec))
    return [x * N for x in vec]

def create_simplex(n_dim):
    """Creates a simplex that has the x axis as a vertex always."""
    simplex = []
    null = [0 for i in xrange(n_dim)]
    v0 = null[:]
    v0[0] = 1
    simplex.append(v0)
    for i in range(1, n_dim):
        tmp = null[:]
        tmp[i] = 1
        tmp2 = average([tmp, v0])
        new_vertex = normalize(tmp2)
        simplex.append(new_vertex)
    return simplex

def find_multivariate_split(data, MIN_LEAF_SIZE, MAX_RUNS = 100):
    """This function looks around the unit sphere to find the unit vector
    that yields the cleanest split in the data set it is given.
    The way the minimization is performed is inspired by the downhill simplex
    method but this time the simplex is constrained to move only on the 
    unit sphere. It works at least in the sense that it finds better splits
    than the univariate splitting."""

    # sorry no convergence criterion yet ... set MAX_RUNS to different value
    n_dim = len(data[0]) - 1

    # python can be used to define 'inner functions' ... 
    def f(u):
        data.sort(key = lambda x: inner(u, x))
        g, sp_idx = find_split(data, MIN_LEAF_SIZE)
        return g, sp_idx
    
    initial_guess = create_simplex(n_dim)
    
    scored_simplex = []
    for v in initial_guess:
        tmp = f(v)
        scored_simplex.append((tmp[0], v, tmp[1]))

    scored_simplex.sort()
    for i in range(MAX_RUNS):
        worst = scored_simplex.pop(-1) # tuple: (worst score, vector)        
        centroid = normalize(average([v[1] for v in scored_simplex]))
        
        trial_vector_1 = mirror(worst[1], centroid)
        trial_score_1, trial_sp_idx_1 = f(trial_vector_1)
        if trial_score_1 < scored_simplex[0][0]:
            trial_vector_2 = mirror(centroid, trial_vector_1)
            trial_score_2, trial_sp_idx_2 = f(trial_vector_2)
            if trial_score_2 < trial_score_1:
                scored_simplex.append((trial_score_2, trial_vector_2, trial_sp_idx_2))
            else:
                scored_simplex.append((trial_score_1, trial_vector_1, trial_sp_idx_1))
        else:
            trial_vector_2 = normalize(average([trial_vector_1, centroid]))
            trial_score_2, trial_sp_idx_2 = f(trial_vector_2)
            if trial_score_2 < scored_simplex[0][0]:
                scored_simplex.append((trial_score_2, trial_vector_2, trial_sp_idx_2))
            else: # shrink the whole simplex
                scored_simplex.append(worst)
                best = scored_simplex.pop(0)
                tmp = []
                for v in scored_simplex:
                    n = normalize(average([best[1], v[1]]))
                    score, sp_idx = f(n)
                    tmp.append((score, n, sp_idx))
                scored_simplex = tmp
                scored_simplex.append(best)
        scored_simplex.sort()
    return scored_simplex[0][0], scored_simplex[0][1], scored_simplex[0][2]

