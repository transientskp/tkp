# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""This file contains some examples of how to use the Pymori library.
These examples are of course contrived and have no bearing on the accuracy of
the various methods demonstrated."""
from __future__ import division
import dataset, user, random

def validate(data, c):
    ok = 0
    for vec in data:
        if c.run(vec)[0] == vec[-1]: ok += 1
    return 1 - ok / len(data)

if __name__ == "__main__":
    d = dataset.set1(1000)
    idx = int(0.9 * len(d))
    
    trials = []
    oob = []
    for i in range(100):
        random.shuffle(d)
        t_d = d[0:idx]
        v_d = d[idx:len(d)]
        fc = user.RF_RC(t_d, 2, 5, 10, 2, 4)
        err = validate(v_d, fc)
        trials.append(err)
        oob.append(fc.fc.oob_error_estimate)
    print len(oob), len(trials)
