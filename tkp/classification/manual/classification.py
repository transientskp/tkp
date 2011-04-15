from .classifier import ClassifiedTransient, Branch


"""

This file defines the various transients that can be classified. It
does so by creating classes that inherit from ClassifiedTransient, and
that define test methods. Each test method can check for one or more
Transient attributes, and returns a weight depending on the outcome
(there is no need to return a default value of 0.0: just let the
method return automatically return None if the checks don't pass.

As an extra option, branches can be introduced, which can bypass
entire classification tests. These are created by defining a subclass
of Branch, and creating test methods. Each test method should return a
list, either empty or consisting of classes; those classes are, again,
subclasses of ClassifiedTransients or Branch, and will be run next
when the code is executed. Branches can thus be nested.

The test method names, for both ClassifiedTransient and Branch
subclasses, should start with 'test', extended by any legimate
character combination (much like the unittest framework). The test
method are not guaranteed to be run in order, and should thus not be
dependent on each other.

"""


class SlowTransient(ClassifiedTransient):

    """Slow transient"""

    def test_duration(self):
        if self.duration > 1e6:
            return 0.9

    def test_variability(self):
        if self.variability > 1e4:
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


class MainBranch(Branch):

    def test1(self):
        return [SubBranch1]

    def test2(self):
        return [SubBranch2]


class SubBranch1(Branch):

    def test1(self):
        return [SlowTransient]


class SubBranch2(Branch):

    def test1(self):
        return [GRBPrompt]


class SpectralBranch(Branch):

    """Spectral branch"""

    def test1(self):
        if self.transient.spectralindex < 0:
            return [SlowTransient, GRBPrompt]
        return []
