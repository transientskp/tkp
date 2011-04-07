# By Thijs Coenen for the LOFAR Transients Key Project may to july 2007, iteration 8
from __future__ import division
import multivariate
try:
    from xml.etree import ElementTree as ET
except:
    from elementtree import ElementTree as ET
from univariate import find_split, signal_to_noise

SIGNAL = 1
NOISE = 0

class tree_classifier(object):
    """The classifier itself, wraps the tree built by tree_builder.py"""
    def __init__(self, tree):
        self.tree = tree
    def run(self, vector):
        return self.check(self.tree, vector)
    def check(self, node, vector):   
        if isinstance(node, univariate_split):
            if vector[node.axis] > node.split:
                return self.check(node.right, vector)
            else:
                return self.check(node.left, vector)
        elif isinstance(node, multivariate_split):
            if multivariate.inner(node.unit, vector) > node.split:
                return self.check(node.right, vector)
            else:
                return self.check(node.left, vector)
        elif isinstance(node, leaf_node):
            return node.classification
        else:
            print "WTF!"

def dot_graph(tree, f):
    f.write("digraph G {\n")
    dot_node(tree, f)
    f.write("}\n")

def dot_node(node, f):
    if isinstance(node, multivariate_split) or isinstance(node, univariate_split):
        f.write("""%(n1)d -> %(n2)d\n""" % {"n1" : node.figno, "n2" : node.left.figno})
        f.write("""%(n1)d -> %(n2)d\n""" % {"n1" : node.figno, "n2" : node.right.figno})
        dot_node(node.left, f)
        dot_node(node.right, f)

def tree_to_xml(tree, f):
    root = ET.Element("decision_tree")
    to_element(tree, root)
    elementtree = ET.ElementTree(root)
    elementtree.write(f)
    return
    
def to_element(node, root):
    if isinstance(node, multivariate_split):
        xml_node = ET.Element("multivariate")
        xml_node.attrib["id"] = str(node.figno)
        xml_node.attrib["unit"]  = str(node.unit)
        xml_node.attrib["split"] = str(node.split)
        xml_node.attrib["left_child_id"] = str(node.left.figno)
        xml_node.attrib["right_child_id"] = str(node.right.figno)
        root.append(xml_node)
        to_element(node.left, root)
        to_element(node.right, root)
    elif isinstance(node, univariate_split):
        xml_node = ET.Element("univariate")
        xml_node.attrib["id"] = str(node.figno)
        xml_node.attrib["axis"]  = str(node.axis)
        xml_node.attrib["split"] = str(node.split)
        xml_node.attrib["left_child_id"] = str(node.left.figno)
        xml_node.attrib["right_child_id"] = str(node.right.figno)
        root.append(xml_node)
        to_element(node.left, root)
        to_element(node.right, root)
    elif isinstance(node, leaf_node):
        xml_node = ET.Element("leaf")
        xml_node.attrib["classification"] = str(node.classification)
        xml_node.attrib["id"] = str(node.figno)
        root.append(xml_node)
    else:
        print "should not appear on screen, this message that is"
        print node.__class__
    return
# -------

class counter(object):
    """Convenience class that is used to get unique node ids"""
    def __init__(self):
        self.counter = 0
    def next(self):
        self.counter += 1
        return self.counter

class leaf_node(object):
    def __init__(self, figno, P):
        self.figno = figno
        if P > 0.5:
            self.classification = SIGNAL
        else:
            self.classification = NOISE

class multivariate_split(object):
    def __init__(self, figno, unit, split, left_child, right_child):
        self.unit = unit
        self.split = split
        self.left = left_child
        self.right = right_child
        self.figno = figno

class univariate_split(object):
    def __init__(self, figno, axis, split, left_child, right_child):
        self.split = split
        self.axis = axis
        self.left = left_child
        self.right = right_child
        self.figno = figno

# ------------------------------------------------------------------------------
# - Interesting stuff follows (the tree induction algorithm):


def empty(*whatever):
    pass

def construct_tree(data, counter, callback = empty, MAX_DEPTH = 5, MIN_LEAF_SIZE = 5, depth = 0):
    """constructs a decision tree, result must be wrapped by a tree_classifier object to be usable
    uses both uni and multivariate splits"""
    n_dim = len(data[0]) - 1
    P = signal_to_noise(data)
    current_gini = P * (1 - P) * len(data)
    figno = counter.next()
    
    # some debugging code that plots node contents for each decision node
    # will probably be ripped out later :
    callback(data, figno, depth, current_gini)

    # stop further branching if: 
    if depth == MAX_DEPTH or P == 0 or P == 1 or len(data) <= MIN_LEAF_SIZE:
        return leaf_node(figno, P)
    best_gini = len(data) 
    # len(data) is larger than the gini of any calculated split so it is safe as
    # a first guess at the new gini (too low a first guess would be a problem)
    
    # univariate splitting:
    for i in range(n_dim):
        data.sort(key = lambda x: x[i])
        new_gini, idx = find_split(data, MIN_LEAF_SIZE)
        new_split = (data[idx][i] + data[idx + 1][i]) / 2
        if new_gini < best_gini:
            best_gini = new_gini
            best_split = new_split
            best_i = i
            split_after = idx
            criterion_uni = ("univariate", best_i, best_split)

    # multivariate splitting:
    g, u, s = multivariate.find_multivariate_split(data, MIN_LEAF_SIZE)
    criterion_multi = ("multivariate", u, (multivariate.inner(data[s][0:-1], u) + multivariate.inner(data[s+1][0:-1], u)) / 2)
    # now use the best split and recurse:

    if best_gini < current_gini and best_gini < g: # univariate split is best
        data.sort(key = lambda x: x[best_i])
        return univariate_split(figno, best_i, best_split, 
            construct_tree(data[0:split_after+1], counter,  callback, MAX_DEPTH, MIN_LEAF_SIZE, depth + 1),
            construct_tree(data[split_after+1:len(data)], counter,  callback, MAX_DEPTH, MIN_LEAF_SIZE, depth + 1))

    elif g < current_gini: # multivariate split is best:
        data.sort(key = lambda x: multivariate.inner(u, x))
        return multivariate_split(figno, u, 
        (multivariate.inner(data[s][0:-1], u) + multivariate.inner(data[s+1][0:-1], u)) / 2,
        construct_tree(data[0 : s + 1 ], counter,  callback, MAX_DEPTH, MIN_LEAF_SIZE, depth + 1),
        construct_tree(data[s + 1 : len(data)], counter,  callback, MAX_DEPTH, MIN_LEAF_SIZE, depth + 1))
    else:
        return leaf_node(figno, P)


def construct_tree_uni(data, counter, callback = empty, MAX_DEPTH = 5, MIN_LEAF_SIZE = 5, depth = 0):
    """constructs a decision tree, result must be wrapped by a tree_classifier object to be usable
    uses both only univariate splits"""
    n_dim = len(data[0]) - 1
    P = signal_to_noise(data)
    current_gini = P * (1 - P) * len(data)
    figno = counter.next()
    
    # some debugging code that plots node contents for each decision node
    # will probably be ripped out later :
    callback(data, figno, depth, current_gini)

    # stop further branching if: 
    if depth == MAX_DEPTH or P == 0 or P == 1 or len(data) <= MIN_LEAF_SIZE:
        return leaf_node(figno, P)
    best_gini = len(data) 
    # len(data) is larger than the gini of any calculated split so it is safe as
    # a first guess at the new gini (too low a first guess would be a problem)
    
    # univariate splitting:
    for i in range(n_dim):
        data.sort(key = lambda x: x[i])
        new_gini, idx = find_split(data, MIN_LEAF_SIZE)
        new_split = (data[idx][i] + data[idx + 1][i]) / 2
        if new_gini < best_gini:
            best_gini = new_gini
            best_split = new_split
            best_i = i
            split_after = idx
            criterion_uni = ("univariate", best_i, best_split)

    if best_gini < current_gini: # univariate split is best
        data.sort(key = lambda x: x[best_i])
        return univariate_split(figno, best_i, best_split, 
            construct_tree(data[0:split_after+1], counter,  callback, MAX_DEPTH, MIN_LEAF_SIZE, depth + 1),
            construct_tree(data[split_after+1:len(data)], counter,  callback, MAX_DEPTH, MIN_LEAF_SIZE, depth + 1))
    else:
        return leaf_node(figno, P)




# ------------------------------------------------------------------------------
# - Uninteresting testing code follows:
        
if __name__ == "__main__":
    import test
    test.test()
    
