from __future__ import division
import dataset

from xml.etree import ElementTree as ET
import random

class leaf_node(object):
    pass

class univariate_split(object):
    pass

class multivariate_split(object):
    pass

def inner(vec1, vec2):
    n_dim = len(vec1)
    return sum([vec1[i] * vec2[i] for i in xrange(n_dim)])

def nodes(tmp):
    nodes = {}
    for element in tmp:
        id = int(element.get("id"))
        if element.tag == "leaf":
            n = leaf_node()
            n.classification = int(element.get("classification"))
            nodes[id] = n
        elif element.tag == "multivariate":
            n = multivariate_split()
            n.left_child_id = int(element.get("left_child_id"))
            n.right_child_id = int(element.get("right_child_id"))
            n.unit = eval(element.get("unit"))
            n.split = float(element.get("split"))
            nodes[id] = n
        elif element.tag == "univariate":
            n = univariate_split()
            n.axis = int(element.get("axis"))
            n.split = float(element.get("split"))
            n.left_child_id = int(element.get("left_child_id"))
            n.right_child_id = int(element.get("right_child_id"))
            nodes[id] = n
    return nodes
    
def build_tree_from_nodes(nodes, idx = 1):
    if isinstance(nodes[idx], leaf_node):
        return nodes[idx]
    elif isinstance(nodes[idx], univariate_split) or isinstance(nodes[idx], multivariate_split):
        nodes[idx].left = build_tree_from_nodes(nodes, nodes[idx].left_child_id)
        nodes[idx].right = build_tree_from_nodes(nodes, nodes[idx].right_child_id)
        del nodes[idx].left_child_id
        del nodes[idx].right_child_id
        return nodes[idx]

class tree_classifier(object):
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
            if inner(node.unit, vector) > node.split:
                return self.check(node.right, vector)
            else:
                return self.check(node.left, vector)
        elif isinstance(node, leaf_node):
            return node.classification
        else:
            print "WTF!"        

def misclassification_rate(data, classifier):
    tmp_sum = 0
    for v in data:
        if classifier.run(v) != v[-1]:
            tmp_sum += 1
    return tmp_sum / len(data)

if __name__ == "__main__":
    tmp = ET.ElementTree(file="nodes.xml")
    r = tmp.getroot()
    tmp2 = nodes(r)
    T = build_tree_from_nodes(tmp2, 1)
    C = tree_classifier(T)
    #print C.run((1,1))
    test_data = dataset.set5(100)
    print "correctly classified", (1 -misclassification_rate(test_data, C)) * 100,"%"
    
