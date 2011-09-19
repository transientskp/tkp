from tkp.classification.manual.classifier import ClassifiedTransient, Branch


"""

This file defines the various transients that can be classified. It
does so by creating classes that inherit from ClassifiedTransient, and
that define test methods. Each test method can check for one or more
Transient attributes, and returns a weight depending on the test
outcome (there is no need to return a default value of 0.0: just let
the method return automatically if the checks don't pass; the
implicitly returned 'None' will be regarded as 0.0).

The test method names, for both ClassifiedTransient and Branch
subclasses, should start with 'test', extended by any legimate
character combination (much like the unittest framework). The test
method are not guaranteed to be run in order, and should thus not be
dependent on each other.  When multiple test are executed, the various
return values (weights) are added together, to result in a single
weight for the specific classified transient.

To start the classification tests for a transient, call the classify()
method (defined in ClassifiedTransient). It will run the various
tests, and return a single-item list with a tuple containing the doc
string of the ClassifiedTransient subclass, and the weight as the
second tuple item (an example returned value could be
[("some transient", 0.6)]). The results are returned as a list because
other classify() methods will be able to extend that list: a single
transient can thus have multiple classification.

As an extra option, branches can be introduced, which can bypass
entire classification tests. These are created by defining a subclass
of Branch, and creating test methods. Each test method should return a
list, either empty or consisting of classes; those classes are, again,
subclasses of ClassifiedTransients or Branch, and will be called when
the code is executed; branches can thus be nested. The returned value
will, in the end, be a list of 2-tuples with a description string and
a weight for each ClassifiedTransient.

"""


class SlowTransient(ClassifiedTransient):

    """Slow transient"""

    def test_duration(self):
        if self.duration > 1e6:
            return 0.9

    def test_variability(self):
        if self.variability > 1e4:
            return 0.9


class FastTransient(ClassifiedTransient):

    """Fast transient"""

    def test_duration(self):
        if self.duration < 1e3:
            return 0.9

    def test_variability(self):
        if self.variability < 1e2:
            return 0.9


class GRBPrompt(ClassifiedTransient):

    """GRB prompt emission"""

    def test_duration(self):
        if 1 < self.duration < 1e4:
            return 0.6

    def test_voevent_delay(self):
        if 0 < self.vo_event.delay < 1e5:
            return 0.6

    def test_variability(self):
        if 0 < self.variability < 1e3:
            return 0.6

class DatabaseSource(ClassifiedTransient):

    """Any transient that can be associated with a database"""

    def test_database(self):
        if len(self.database):
            return 1.0
    

class SubBranch1a(Branch):

    def test1(self):
        return [SlowTransient]


class SubBranch1b(Branch):

    def test1(self):
        return [FastTransient]


class SubBranch2(Branch):

    def test1(self):
        return [GRBPrompt]


class SpectralBranch(Branch):

    """Negative spectral index"""

    def test1(self):
        if self.transient.spectralindex < 0:
            return [SlowTransient, GRBPrompt]
        return []


class Main(Branch):

    """Starting point for manual classification tree"""
    
    def test1(self):
        return [SubBranch1a, SubBranch1b]

    def test2(self):
        return [SubBranch2]

    def test3(self):
        return [DatabaseSource]
    

