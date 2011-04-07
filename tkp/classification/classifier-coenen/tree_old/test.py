from __future__ import division
from tree_builder import *
import pylab, dataset

"""Some testing code, still remains messy."""


def misclassification_rate(data, classifier):
    """Calculates the misclassification rate of a classifier, the 
    classifier is assumed to be an object that has a .run member function.
    
    input:
    data is a list of tuples, where the last element of the tuple is the
    correct class designation.
    
    output:
    the fraction that is misclassified
    """
    tmp_sum = 0
    for v in data:
        if classifier.run(v) != v[-1]:
            tmp_sum += 1
    return tmp_sum / len(data)

def show_2d_plot(data, classifier):
    """Runs a classifier comparing the class designations of the data tuples
    and the output of the classifier for those vectors. Then it draws a graph
    of the results."""
    pylab.figure(-1)
    l = []
    for v in data:
        l.append(classifier.run(v))

    pylab.plot([data[i][0] for i in range(len(data)) if data[i][-1] == SIGNAL and SIGNAL == l[i]], 
    [data[i][1] for i in range(len(data)) if data[i][-1] == SIGNAL and SIGNAL == l[i]], "ro")
    
    pylab.plot([data[i][0] for i in range(len(data)) if data[i][-1] == SIGNAL and NOISE == l[i]], 
    [data[i][1] for i in range(len(data)) if data[i][-1] == SIGNAL and NOISE == l[i]], "ko")

    pylab.plot([data[i][0] for i in range(len(data)) if data[i][-1] == NOISE and SIGNAL == l[i]], 
    [data[i][1] for i in range(len(data)) if data[i][-1] == NOISE and SIGNAL == l[i]], "k.")
    
    pylab.plot([data[i][0] for i in range(len(data)) if data[i][-1] == NOISE and NOISE == l[i]], 
    [data[i][1] for i in range(len(data)) if data[i][-1] == NOISE and NOISE == l[i]], "g.")
    pylab.xlabel("x")
    pylab.ylabel("y")
    pylab.title("test data distribution")
    pylab.savefig("node_everything.png")

def plot_node_contents(data, figno, depth, current_gini):
    """this plots the node contents for each node, uses a global variable 
    containing the whole learning sample to do so (really ugly code wise)"""
    pylab.figure(figno)
    pylab.plot([x[0] for x in NARF], [x[1] for x in NARF], "k.")    
    pylab.plot([x[0] for x in data if x[-1] == NOISE], [x[1] for x in data if x[-1] == NOISE], "bo")
    pylab.plot([x[0] for x in data if x[-1] == SIGNAL], [x[1] for x in data if x[-1] == SIGNAL], "co")
    pylab.title("depth = "+str(depth)+"    gini = " +str(current_gini))
    pylab.savefig("node"+str(figno)+".png")

def test():
    import time
    print "creating data set"
    data = dataset.set5(100)
    global NARF
    NARF = data[:]
    print "number of points in learning sample", len(data)
    print "inducing decision tree classifier"
    a = time.time()
    c = counter()
    tree = construct_tree(data, c, plot_node_contents) 
    # by setting the callback function to plot_node_contents, all the datapoints in 
    print "It took", time.time() - a, "seconds to construct the tree."
    classifier = tree_classifier(tree)
    print "running classifier (to calculate resubsitution estimate)"
    print "correctly classified (for resubsituted learning sample!)", (1 - misclassification_rate(data, classifier)) * 100, "%"
    print "plotting resulsts"
    show_2d_plot(dataset.set5(100, 455), classifier)
    print "done"
    f = open("nodes.dot", "w")
    dot_graph(tree, f)
    f.close()   
    f = open("nodes.xml", "w")
    tree_to_xml(tree, f)
    f.close()
