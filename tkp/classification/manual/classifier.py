from .transient import Transient
import os
import  itertools


class Branch(object):
    """A classification branch"""

    def __init__(self, transient, *args, **kwargs):
        self.transient = transient
        self.results = []
        super(Branch, self).__init__(*args, **kwargs)

    def classify(self):
        tests = list(itertools.ifilter(
            lambda x: x.startswith('test'), dir(self)))
        for test in tests:
            try:
                for classification in (getattr(self, test))():
                    self.results.extend(
                        classification(self.transient).classify())
            except AttributeError:
                pass
        return self.results


class ClassifiedTransient(Transient):
    """A classified transient"""

    def __init__(self, *args, **kwargs):
        """Initialize with either a Transient object, or all the separate
        transient attributes"""

        if len(args) > 0 and isinstance(args[0], Transient):
            t = args[0]
            args = (t.srcid, t.duration, t.variability, t.database, t.position,
                    t.timezero, t.shape, t.spectralindex) + args[1:]
        super(ClassifiedTransient, self).__init__(*args, **kwargs)

    def classify(self):
        """Obtain and run the test for this specific classification"""

        tests = list(itertools.ifilter(
            lambda x: x.startswith('test'), dir(self)))
        weight = 0
        for test in tests:
            try:
                w = (getattr(self, test))()
                if w is not None:
                    weight += w
            except AttributeError:
                pass
        return [(self.__doc__, weight)]


class Classifier(object):

    """
    The Classifier object is your starting point for classification.

    Feed it a Transient object and a starting point ('base'), which can
    either be a ClassifiedTransient subclass, or a Branch subclass. It will
    then follow the logic stream from the base to classify your transient.
    """

    def __init__(self, transient, base, *args, **kwargs):
        """Initialize the classifier with a transient and a classification
        starting point

        arguments

        - transient: a Transient object

        - base: The starting class from which the classification logic follows.
                The base class normally calls several other classes that
                classify various transient.
        """

        self.transient = transient
        self.base = base
        self.classes = []
        self.results = []
        super(Classifier, self).__init__(*args, **kwargs)

    def classify(self):
        self.results = self.base(self.transient).classify()
        return self.results
