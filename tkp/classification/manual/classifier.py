"""

Classify a Transient object, according to a user classification tree.

.. module::
   :synposis: Classify a Transient object, according to a user classification tree.
   
.. moduleauthor: Evert Rol, Transient Key Project <software@transientskp.org>


The actual classification work is done here, in three parts:

- The Classifier class picks up the transient and classification tree

- The Branch will step through the tree, adding points (weights) to
  the classification of the Transient instance

- The ClassifiedTransient instance will compare each criterion with
  the value of the Transient instance

"""


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
        """Classify the transient by stepping through the classification
        tree"""
        
        tests = list(itertools.ifilter(
            lambda x: x.startswith('test'), dir(self)))
        for test in tests:
            try:
                for classification in (getattr(self, test))():
                    self.results.extend(
                        classification(self.transient).classify())
            except (AttributeError, TypeError) as e:
                pass
        return self.results


class ClassifiedTransient(Transient):
    """A classified transient"""

    def __init__(self, *args, **kwargs):
        """Initialize with either a Transient object, or all the separate
        transient attributes"""

        if len(args) > 0 and isinstance(args[0], Transient):
            args = list(args)
            t = args.pop(0)
            newkwargs = {}
            for key in ('duration', 'variability', 'database', 'position',
                        'timezero', 'shape', 'spectralindex'):
                try:
                    newkwargs[key] = getattr(t, key)
                except AttributeError:
                    newkwargs[key] = None
            # supplied kwargs override values of the transient object
            newkwargs.update(kwargs)
            args.insert(0, t.srcid)
        super(ClassifiedTransient, self).__init__(*args, **newkwargs)

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
            except (AttributeError, TypeError) as e:
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

        :argument transient: the transient to be classified
        :type transient: Transient
        :argument base: The starting class from which the
            classification logic follows.  The base class normally
            calls several other classes that classify various
            transient.
        :type base: (sub)class of Branch
        """

        self.transient = transient
        self.base = base
        self.classes = []
        self.results = []
        super(Classifier, self).__init__(*args, **kwargs)

    def classify(self):
        """Start the actual classification

        :returns: weights for each possible classification: each tuple
            containing a description and a weight
        :rtype: list of two-tuples
        """
        
        self.results = self.base(self.transient).classify()
        return self.results
