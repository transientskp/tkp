# Set up the classification system.
# Normally, this would be done in an external file (module), but that
# would complicate things, since we would have to set the TKPCONFIGDIR
# environment variable, and that module would have to be called
# classification.py, the same name as this unit test.
from tkp.classification.manual.classifier import Branch
from tkp.classification.manual.classifier import ClassifiedObject


class ShortTransient(ClassifiedObject):
    """Short duration transient"""

    def test_duration(self):
        if self.duration < 1e3:
            return 0.9


class ShortRapidTransient(ClassifiedObject):
    """Short duration, high activity transient"""

    def test_activity(self):
        if self.activity > 0.5:
            return 0.9

    def test_duration(self):
        if self.duration < 1e3:
            return 0.9


class ShortSlowTransient(ClassifiedObject):
    """Short duration, low activity transient"""

    def test_activity(self):
        if self.activity < 0.5:
            return 0.9

    def test_duration(self):
        if self.duration < 1e3:
            return 0.9


class LongTransient(ClassifiedObject):
    """Long duration transient"""

    def test_duration(self):
        if self.duration > 1e3:
            return 0.9


class LongRapidTransient(ClassifiedObject):
    """Long duration, high activity transient"""

    def test(self):
        if self.activity > 0.5 and self.duration > 1e3:
            return 0.9


class LongSlowTransient(ClassifiedObject):
    """Long duration, low activity transient"""

    def test(self):
        if self.activity <= 0.5 and self.duration > 1e3:
            return 0.9


class RapidTransient(ClassifiedObject):
    """High activity transient"""

    def test(self):
        if self.activity > 0.5:
            return 0.9

        
class SlowTransient(ClassifiedObject):
    """Low activity transient"""

    def test(self):
        if self.activity > 0.5:
            return 0.9

        
class ShortDurationBranch(Branch):
    """Branch on short transients"""

    def test_duration(self):
        if self.duration < 1e3:
            self.eval(RapidTransient, SlowTransient)
            return 0.9


class LongDurationBranch(Branch):
    """Branch on short transients"""

    def test_duration(self):
        if self.duration > 1e3:
            self.eval(RapidTransient, SlowTransient)
            return 0.9


class DurationBranch(Branch):
    """Branch on short/long transient duration"""

    def test_duration(self):
        if self.duration < 1e3:
            self.eval(ShortTransient, ShortRapidTransient, ShortSlowTransient)
        else:
            self.eval(LongTransient, LongRapidTransient, LongSlowTransient)


class Main(Branch):
    """Starting point"""

    def test(self):
        self.eval(DurationBranch)
