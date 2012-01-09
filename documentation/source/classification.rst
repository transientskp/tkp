.. _classification:

Classification
==============

Attempt to classify the detected transients into one or more groups.

- inputs:

  - weight_cutoff: set a cutoff: any classified transient with a
    total classification weight below this value will not be output.

  - transients: list of :ref:`Transient
    <tkpapi:classification-manual-transient>` objects,
    previously obtained with the transient_search recipe.

  - nproc: number of maximum simultaneous processors per node.

- outputs:

  - transients: list of :ref:`Transient
    <tkpapi:classification-manual-transient>` objects,
    amended with their classification.



Creating your own manual classification
---------------------------------------

By default, the classification recipe takes its classification (a
simple decision tree) from the :ref:`classification module
<tkpapi:classification-manual-classification>`. To create your own
decision tree, you have to create a simple Python file named
:file:`classification.py` in the default TKP configuration directory
(:file:`$HOME/.transientskp/`).

The contents of the Python file is a set of classes, where each class
is either the final outcome of the decision tree or a branch into a
further (sub)classification. Inside each class, there are one or more
methods that start their name with `test` which test for
characteristics of a specific transient using a simple `if`
statement. Each method returns a weight (0.0 by default, eg if the
`if` statement does not pass), and the added value of the weights
combine to the total weight of that specific classification.

A few examples should be clearer. Let's start with the `Main` class,
which is the mandatory starting point. This will be a branch, so it
inherits from :py:class:`~tkp.classification.manual.classifier.Branch`. The
`Main` class has two `test` methods (simply named `test1` and
`test2`), which symbolize the two branches of the tree. Each branch
returns a list of classes it wants to test; in this example, these
will be classification classes, not subbranches::

    from tkp.classification.manual.classifier import Branch

    class Main(Branch):
        """Starting point for the classification tree"""

        def test1(self):
            return [Transient1]

        def test2(self):
            return [Transient2]


Now we need to define the `Transient1` and `Transient2`
classifications. Let's simply classify on the duration of the
transient: one is for short transients, the second for long
transients; any duration in between will have no classification::

    from tkp.classification.manual.classifier import ClassifiedTransient

    class Transient1(ClassifiedTransient):
        """Short duration transient"""

        def test_duration(self):
            if self.duration < 1e3:
                return 1.0

    class Transient2(ClassifiedTransient):
        """Long duration transient"""

        def test_duration(self):
            if self.duration > 1e5:
                return 1.0

The `duration` attribute (`self.duration`) is automatically obtained
by inheriting from
:py:class:`~tkpapi:tkp.classification.manual.classifier.ClassifiedTransient`
or :py:class:`~tkpapi:tkp.classification.manual.classifier.Branch`: all
features obtained in the :ref:`feature extraction recipe
<feature_extraction>` are available this way in the classification
tree.

We can also create branches dependent on the duration, instead of
direct classifications; on the branches, we classify transients on
other characteristics, but the duration is already implicit. Since
multiple classifications are possible, we can have global and specific
classifications at the same; the latter will have more weight, and
thus be at the top of the resulting classifications when ordered by
weight.

::


    from tkp.classification.manual.classifier import Branch
    from tkp.classification.manual.classifier import ClassifiedTransient


    class ShortTransient(ClassifiedTransient):
        """Short duration transient"""

        # There is no real need to test for the duration; 
        # this has already been done by branching.
        # It could be, however, that this class is called by itself, 
        # i.e., not through the DurationBranch.
        def test_duration(self):
            if self.duration < 1e3:
                return 1.0


    class ShortRapidTransient(ClassifiedTransient):
        """Short duration, rapid variability transient"""

        # Note that, since we do not check for duration,
        # this class can only be called through the DurationBranch
        def test_variability(self):
            if self.variability > 0.1:
                return 1.0

        # We do not actually check for the duration, so this class can
        # only be called by the DurationBranch. We still need to
        # return an appropriate weight, though.
        # See also the comment for the LongTransient
        def test_duration(self):
            return 1.0


    class ShortSlowTransient(ClassifiedTransient):
        """Short duration, slow variability  transient"""

        # Note that, since we do not check for duration,
        # this class can only be called through the DurationBranch
        def test_variability(self):
            if self.variability < 0.1:
                return 1.0

        # We do not actually check for the duration, so this class can
        # only be called by the DurationBranch. We still need to
        # return an appropriate weight, though.
        # See also the comment for the LongTransient
        def test_duration(self):
            return 1.0


    class LongTransient(ClassifiedTransient):
        """Long duration transient"""

        # There is no real need to test for the duration; 
        # this has already been done by branching.
        # It could be, however, that this class is called by itself, 
        # i.e., not through the DurationBranch.
        # If we do not check for duration, we should have at least one 
        # `test` method that returns the an appropriate weight.
        def test_duration(self):
            if self.duration > 1e3:
                return 1.0


    class LongRapidTransient(ClassifiedTransient):
        """Long duration, rapid variability transient"""

        def test_variability(self):
            if self.variability > 0.1:
                return 1.0

        # We do not actually check for the duration, so this class can
        # only be called by the DurationBranch. We still need to
        # return an appropriate weight, though.
        # See also the comment for the LongTransient
        def test_duration(self):
            return 1.0


    class LongSlowTransient(ClassifiedTransient):
        """Long duration, slow variability  transient"""

        def test_variability(self):
            if self.variability < 0.1:
                return 1.0

        # We do not actually check for the duration, so this class can
        # only be called by the DurationBranch. We still need to
        # return an appropriate weight, though.
        # See also the comment for the LongTransient
        def test_duration(self):
            return 1.0


    class DurationBranch(Branch):
        """Branch on short/long transient duration"""

        def test_duration(self):
            if self.duration < 1e3:
                return [ShortTransient, ShortRapidTransient, ShortSlowTransient]
            else:
                return [LongTransient, LongRapidTransient, LongSlowTransient]

    class Main(Branch):
        """Starting point"""

        def test(self):
            return [DurationBranch]


We could have made the branching on the duration happen in the Main
branch in the above example, but haven't done so for the clarity of
the example.

Note the extra `test_duration` methods that do not have the actual
duration check, since this is already done at the branch level.

The final result of the classification is a dictionary with the
weights for each classification (only the weights above the cutoff
level specified by the `weight_cutoff` input parameter are shown).

The *class docstrings* are actually important here: these are the
dictionary *keys* of the resulting classification dictionary. The
dictionary values are the combined weights. For example, a
short and rapidly varying transient would have the following
classifications using the above scheme::

    {'Short duration, rapid variability transient': 2.0,
     'Short duration transient': 1.0}
