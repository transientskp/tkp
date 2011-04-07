# Text classification demo :) Trivial demo of how a classifier might work.

from string import *
from broker import *

class file_contents(object):
    """Object to hold contents of a file, """
    def __init__(self, file_name):
        self.file_name = file_name
        self.metadata = metadata(None, None, None, None, None)
        try:
            f = open(file_name, "r")
            self.contents = f.read()
            f.close()
        except:
            self.contents = ""

class ascii_histogram(object):
    pass

def create_ascii_histogram_from_file(dict):
    out = []
    for X in dict[file_contents]:
        histogram = {}
        total = 0
        for x in ascii_lowercase:
            histogram[x] = 0
        for x in X.contents:
            if lower(x) in ascii_lowercase:
                histogram[lower(x)] += 1
                total += 1
        tmp = ascii_histogram()
        tmp.histogram = histogram
        tmp.total = total
        tmp.metadata = metadata(None, None, None, None, X.file_name)
        out.append(tmp)
    return out

def create_ascii_histogram_from_string(some_string):
    histogram = {}
    total = 0
    for x in ascii_lowercase:
        histogram[x] = 0
    for x in some_string:
        if lower(x) in ascii_lowercase:
            histogram[lower(x)] += 1
            total += 1
    tmp = ascii_histogram()
    tmp.histogram = histogram
    tmp.total = total
    tmp.metadata = metadata(None, None, None, None, "TEMPORARY")
    return [tmp]

def score(A, B):
    assert isinstance(A, ascii_histogram)
    assert isinstance(B, ascii_histogram)
    D = 0
    for k in ascii_lowercase:
        D += (A.histogram[k] / float(A.total) - B.histogram[k] / float(B.total))**2
    return D

class classifier_zero(object):
    def __init__(self):
        # this function sets up the broker object
        b = broker()
        NS = naive_memory_store()
        b.register_store(file_contents, NS.store)
        b.register_retrieve(file_contents, NS.retrieve)
        b.register_create(ascii_histogram, create_ascii_histogram_from_file, [file_contents])
        b.register_store(ascii_histogram, NS.store)
        b.register_retrieve(ascii_histogram, NS.retrieve)
        self.broker = b
    def test(self):
        s = raw_input("Give me some text >")
        for f in ["en.txt", "nl.txt"]:
            tmp = file_contents(f)
            self.broker.store([tmp])
        self.broker.query(ascii_histogram, None, None, None, None, None)
        user = create_ascii_histogram_from_string(s)[0]
        dict = {"en.txt" : "English", "nl.txt" : "Dutch"}
        l = []
        for k in dict:
            tmp = self.broker.query(ascii_histogram, None, None, None, None, k)
            a = score(tmp[0], user)
            l.append((a, dict[k]))
        l.sort()
        print "Classification:", l[0][1]

        
if __name__ == "__main__":
    c = classifier_zero()
    c.test()
