# fake data for tree inducer to work on
import random, math

def set0(N = 100, seed = 10):
    training_data = []
    for i in range(N):
        training_data.append((random.gauss(5, 0.5), 1))
        training_data.append((random.gauss(10, 0.5), 0))
    return training_data

def set1(N = 100, seed = 10):
    random.seed(seed)
    training_data = []
    for i in range(N):
        training_data.append((random.gauss(12, 3), random.gauss(12, 2), 1))
    for i in range(N):
        training_data.append((random.gauss(10, 3), random.gauss(0, 3), 0))
        training_data.append((random.gauss(7, 3), random.gauss(2,3), 0))
        training_data.append((random.gauss(0, 3), random.gauss(10, 3), 0))
        training_data.append((random.gauss(5, 3), random.gauss(5, 3), 0))
    return training_data

def set1_3d(N = 100, seed = 10):
    # for 3d data handling testing ...
    random.seed(seed)
    training_data = []
    for i in range(N):
        training_data.append((random.gauss(12, 3), random.gauss(12, 2), 0, 1))
    for i in range(N):
        training_data.append((random.gauss(10, 3), random.gauss(0,  3), 0, 0))
        training_data.append((random.gauss(7,  3), random.gauss(2,  3), 0, 0))
        training_data.append((random.gauss(0,  3), random.gauss(10, 3), 0, 0))
        training_data.append((random.gauss(5,  3), random.gauss(5,  3), 0, 0))
    return training_data

def set2(N = 100, seed = 10):
    random.seed(seed)
    training_data = []
    for i in range(N):
        training_data.append((random.gauss(-5, 0.5), random.gauss(-5, 0.5), 1))
        training_data.append((random.gauss(-5, 0.5), random.gauss(5, 0.5), 0))
        training_data.append((random.gauss(5, 0.5), random.gauss(-5, 0.5), 0))
        training_data.append((random.gauss(5, 0.5), random.gauss(5, 0.5), 1))
    #training_data.append((random.gauss(-5, 0.5), random.gauss(-5, 0.5), 1))

    return training_data

def set3(N = 100, seed = 10):
    random.seed(seed)
    training_data = []
    for i in range(100):
        training_data.append((random.gauss(-5, 4), random.gauss(-5, 4), 1))
        training_data.append((random.gauss(-5, 4), random.gauss(5, 4), 0))
        training_data.append((random.gauss(5, 4), random.gauss(-5, 4), 0))
    return training_data

def set4(N = 100, seed = 10):
    random.seed(seed)
    t = []
    for i in range(N):
        t.append((random.random() + 1, random.gauss(10, 1), 1))
        t.append((random.random() + 3, random.gauss(10, 1), 0))
        t.append((random.random(), random.gauss(10, 1), 0))
    return t

def set5(N = 100, seed = 10):
    random.seed(seed)
    t = []
    for i in range(N):
        t.append((random.gauss(1,0.5), random.gauss(1,0.5), 1))
        t.append((random.gauss(2,0.5), random.gauss(2,0.5), 1))
        t.append((random.gauss(1,0.5), random.gauss(3,0.5), 0))
        t.append((random.gauss(2,0.5), random.gauss(4,0.5), 0))
        t.append((random.gauss(3,0.5), random.gauss(3,0.5), 0))
    return t


if __name__ == "__main__":
    import pylab
    l = set1()
    pylab.plot([x[0] for x in l if x[2] == 1], [x[1] for x in l if x[2] == 1],
    "ko")
    pylab.plot([x[0] for x in l if x[2] == 0], [x[1] for x in l if x[2] == 0],
    "k.")
    pylab.title("data set 1, created with function set1()")
    pylab.show()