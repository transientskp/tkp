.. _classification:

Classification
==============

Attempt to classify the detected transients into one or more groups.

- inputs:

parset = %(runtime_directory)s/jobs/%(job_name)s/parsets/classification.parset
  - parset: parameter set, currently containing only one parameter:

    - weighting.cutoff: Any classified transient with a total
      classification weight below this value will not be output.

  - nproc: number of maximum simultaneous processors per node.

- outputs:

  - transients: list of :ref:`Transient
    <tkpapi:classification-transient-transient>` objects,
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

        self.eval(Transient1, Transient2)


Now we need to define the `Transient1` and `Transient2`
classifications. Let's simply classify on the duration of the
transient: one is for short transients, the second for long
transients; any duration in between will have no classification::

    from tkp.classification.manual.classifier import ClassifiedObject

    class Transient1(ClassifiedObject):
        """Short duration transient"""

        def test_duration(self):
            if self.duration < 1e3:
                return 1.0

    class Transient2(ClassifiedObject):
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
direct classifications based on duration. On the branches, we classify
transients based on their duration, assign a weight to them if wanted,
and then further classify them using more specific classifiers. This
might look as follows::

    class ShortDurationBranch(Branch):

        def test_duration(self):
            if duration < 1e3:
                # Evaluate all classifications applicable for short transients
                self.eval(Transient3, Transient4, Transient5)
                # Since this is a specific "short duration" branch,
                # we return a score for a short transient
                return 1.0
            else:
                # Evaluate all classifications applicable for long transients
                # Obviously, some classifications are applicable for both types
		self.eval(Transient5, Transient6)

But if you don't want to make things complicated, you can thus
evaluate all separate classification classes, without branches (other
than the initial Main branch to start from).

The final result of the classification is a dictionary with the
weights for each classification (only the weights above the cutoff
level specified by the `weight_cutoff` input parameter are shown in
the final output).

The *class docstrings* are actually important here: these are the
dictionary *keys* of the resulting classification dictionary. The
dictionary values are the combined weights. For example, a
short and rapidly varying transient would have the following
classifications using the above scheme::

    {'Short duration, rapid variability transient': 2.0,
     'Short duration transient': 1.0}


Available features
------------------

In the above classification module, features are accessible as
attributes of `self`, like `self.duration` and `self.variability`. The
TKP library tries to extract such features in the
:ref:`tkpapi:features` module. The following features are available:

`duration`
  full duration of the transient

`variability`
  a measure of the actual activity of the transient. It
  is the ratio of the amount of time the transient light curve is
  above background level, to the full duration of the transient. It is
  always equal or smaller than 1.

`position`
  a :py:class:`tkpapi:tkp.classification.manual.utils.Position` object,
  and has a `match` method to match with another `Position`
  object. `Position` objects have an `RA`, `Dec` and an uncertainty on
  the position.

`timezero`
  the starting point of the transient, which is a
  :py:class:`tkpapi:tkp.classifiation.manual.utils.DateTime` object,
  and has a `match` method to match with another `DateTime`
  object. `DateTime` objects are very similar to the standard python
  `datetime.datetime` objects, but have an extra `error` attribute
  that indicates the accuracy of the time stamp in seconds.

`database`
  a list of databases that are matched. For each matched
  database, the list item is a dictionary with the database name
  (abbreviation) as the key, and another (sub)dictionary as the
  value. This subdictionary contains the information about the best
  matched source, such as its `ra` and `dec`, the (dimensionless)
  association parameter `assoc_r`, the source identifier in the
  catalog `catsrcname` etc.


Finally, there is a dictionary attribute called `features`, which
contains all of the above features plus several others (note: at the
moment, the `database` list is not yet included here). While this may
seem a bit redundant, the point of this `features` attribute is that
it can easily be used by any automated classification routine, by
translating the dictionary into a feature vector that can be fed into
these classification routines.

The `features` attributes currently contains the following data:

`wkurtosis`
   (flux error) weighted kurtosis value

`wskew`
  (flux error) weighted skew value

`wstddev`
  (flux error) weighted standard deviation

`wmean`
  (flux error) weighted mean

`median`
  median flux value 

`max`
  `peakflux`: maximum flux

`relpeakflux`
  relative peak flux (relative to the background value)

`risefallratio`
  ratio between the time of the increase to the peak flux, and the
  time of the decrease from peak flux to background level

`duration`
  `variability`
