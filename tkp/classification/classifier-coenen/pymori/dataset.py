# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""This module contains a few fake data sets that can be used to check
the classifiers or to show how to construct them."""
import random, math

def set0(N = 100, seed = 10):
    training_data = []
    t = 0
    for i in range(N):
        training_data.append((random.gauss(5, 0.5), t, 1, 1))
        t += 1
        training_data.append((random.gauss(10, 0.5), t, 1, 0))
    return training_data

def set1(N = 100, seed = 10):
    random.seed(seed)
    training_data = []
    t = 0
    for i in range(N):
        training_data.append((random.gauss(12, 3), random.gauss(12, 2),t, 1, 1))
        t += 1
        training_data.append((random.gauss(10, 3), random.gauss(0, 3),t, 1, 0))
        t += 1
        training_data.append((random.gauss(7, 3), random.gauss(2,3),t, 1, 0))
        t += 1
        training_data.append((random.gauss(0, 3), random.gauss(10, 3),t, 1, 0))
        t += 1
        training_data.append((random.gauss(5, 3), random.gauss(5, 3),t, 1, 0))
        t += 1
    return training_data

def set2(N = 100, seed = 10):
    random.seed(seed)
    training_data = []
    t = 0
    for i in range(N):
        training_data.append((random.gauss(-5, 0.5), random.gauss(-5, 0.5),t, 1, 1))
        t += 1
        training_data.append((random.gauss(-5, 0.5), random.gauss(5, 0.5),t,1, 0))
        t += 1
        training_data.append((random.gauss(5, 0.5), random.gauss(-5, 0.5),t, 1, 0))
        t += 1
        training_data.append((random.gauss(5, 0.5), random.gauss(5, 0.5),t, 1, 1))
        t += 1

    return training_data

def set3(N = 100, seed = 10):
    random.seed(seed)
    training_data = []
    t = 0
    for i in range(100):
        training_data.append((random.gauss(-5, 4), random.gauss(-5, 4), t, 1, 1))
        t += 1
        training_data.append((random.gauss(-5, 4), random.gauss(5, 4), t, 1, 0))
        t += 1
        training_data.append((random.gauss(5, 4), random.gauss(-5, 4), t, 1, 0))
        t += 1
    return training_data

def set4(N = 100, seed = 10):
    random.seed(seed)
    training_data = []
    t = 0
    for i in range(N):
        training_data.append((random.random() + 1, random.gauss(10, 1), t, 1, 1))
        t += 1
        training_data.append((random.random() + 3, random.gauss(10, 1), t, 1, 0))
        t += 1
        training_data.append((random.random(), random.gauss(10, 1), t, 1, 0))
        t += 1
    return training_data

def set5(N = 100, seed = 10):
    random.seed(seed)
    training_data = []
    t = 0
    for i in range(N):
        training_data.append((random.gauss(1,0.5), random.gauss(1,0.5), t, 1, 1))
        t += 1
        training_data.append((random.gauss(2,0.5), random.gauss(2,0.5), t, 1, 1))
        t += 1
        training_data.append((random.gauss(1,0.5), random.gauss(3,0.5), t, 1, 0))
        t += 1
        training_data.append((random.gauss(2,0.5), random.gauss(4,0.5), t, 1, 0))
        t += 1
        training_data.append((random.gauss(3,0.5), random.gauss(3,0.5), t, 1, 0))
        t += 1
    return t

def trivial1():
    """Trivial 2d dataset, mustbe classified 100% correctly."""
    l = [(x, 0, x, 1, 0) for x in xrange(10)]
    l.extend([(x, 0, x, 1, 1) for x in xrange(10, 20)])
    return l

def trivial2():
    """Trivial 2d dataset, mustbe classified 100% correctly."""
    l = [(x, 0, 1, 0) for x in xrange(10)]
    l.extend([(x, 0, x, 1, 1) for x in xrange(10, 15)])
    l.extend([(x, 0, x, 1, 2) for x in xrange(15, 20)])
    return l    

def trivial4():
    """Trivial 2d dataset, must be classified 100% correctly."""
    l = [(random.random(), random.random(), i, 1, 0) for i in xrange(100)]
    l.extend([(random.random()+1, random.random() + 1, i + 100, 1, 1) for i in xrange(100)])
    return l

def trivial5():
    """Trivial 2d dataset, must be classified 100% correctly."""
    l = []
    t = 0
    for ix in range(10):
        for iy in range(10):
            if ix > iy:
                l.append((ix, iy, t, 1, 0))
            elif iy > ix:
                l.append((ix, iy, t, 1, 1))
            t += 1
    return l


if __name__ == "__main__":
    print __doc__