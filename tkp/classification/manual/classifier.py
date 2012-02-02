"""
Classify an object, by parsing it through a user defined decision tree.

This module contains the necessary classes to classify an arbitrary
object, using the decision tree set up in the classification
module. This module can be dynamically imported if necessary, by
storing it in directory given by the path keyword in the Classifier
initializer.

Alternatively, one can run the classifier by pointing it directly at
the entry point of the decision tree.


The actual classification work is done in three parts:

- The Classifier class picks up the object to be classified and the
  main starting point of the decision tree.

- The ClassifiedObject instance will compare each criterion with the
  value of the object attribute, and return a score. The outcomes of
  each comparison are added together to form the total score of that
  ClassifiedObject.

- A Branch behaves similar to a ClassifiedObject, but it evaluates
  multiple ClassifiedObjects, while bypassing a whole other part of
  the tree, based on a criterion. In addition, it can also (like a
  ClassifiedObject) return a score for a whole branch; such a score
  is added to all the individual scores from the evaluated
  ClassifiedObjects.

The object to be classified should have attributes that can be used as
criteria. The `Classifier` will automatically find these attributes
from the object.

"""


import os
import  itertools
import imp
import tkp.config


class ClassifiedObject(object):
    """A classified object"""

    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        super(ClassifiedObject, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.obj, name)
        
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
        return {self.__doc__: weight}


class Branch(ClassifiedObject):
    """A classification branch"""

    def __init__(self, obj, *args, **kwargs):
        self.results = {}
        super(Branch, self).__init__(obj=obj, *args, **kwargs)

    def eval(self, *args, **kwargs):
        """Evaluate a list of (sub)branches or classified object"""

        for classification in args:
            self.results.update(classification(self.obj).classify())

    def __getattr__(self, name):
        return getattr(self.obj, name)
        
    def classify(self):
        """Classify the obj by stepping through the classification
        tree"""

        tests = list(itertools.ifilter(
            lambda x: x.startswith('test'), dir(self)))
        weight = 0
        for test in tests:
            try:
                w  = (getattr(self, test))()
                if w is not None:
                    weight += w
            except (AttributeError, TypeError) as e:
                pass
        results = dict([(k, v+weight) for k, v in self.results.iteritems()])
        return results


class Classifier(object):

    """
    The Classifier object is your starting point for classification.

    Feed it an object to be classified and optionally a starting point
    ('base'), which should be a Branch subclass. It will then follow
    the logic stream from the base to classify your object.
    """

    def __init__(self, obj, base=None, paths=None, *args, **kwargs):
        """Initialize the classifier with an object and a classification
        starting point

        Args:

            obj: the object to be classified

        Kwargs:

            base (Branch or None): The starting class from which the
                classification logic follows.  The base class normally
                calls several other classes that classify various
                objects.

                branch can be a Branch or a subclass thereof, or
                None. In the latter case, the Classifier will try and
                important a starting branch from a classification
                module. This starting branch should be called
                "Main". The imported module should exist in a
                directory given by the paths keyword (see below).

            paths (list of strings): search paths (directories) where
                to look for the user defined classification.py
                module. In case the module is not found in any of the
                given directories, the classification.py module
                relative to this module is imported (which usually
                results in no classifications).

        Raises:

            ImportError, in case the Main branch can't be found.

        """

        self.obj = obj
        self.paths = [] if paths is None else paths
        self.base = self._get_base(base)
        super(Classifier, self).__init__(*args, **kwargs)

    def _get_base(self, base):
        if base is not None:
            return base
        try:
            f, p, d = imp.find_module('classification', self.paths)
            m = imp.load_module('classification', f, p, d)
        except ImportError:
            # Fallback: default classification scheme
            from . import classification as m
        return m.Main

    def classify(self):
        """Start the actual classification

        Returns:

            (dict): weights for each possible classification: the
                dictionary keys are the classification names, and the
                corresponding values are the weights for those
                classifications.
        """

        results = self.base(self.obj).classify()
        return results
