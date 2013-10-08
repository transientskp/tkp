.. _classification-introduction:

++++++++++++
Introduction
++++++++++++

The classification package consists of a few subpackages:

- features: this contains modules that allow the user to extract
  characteristics of found transients. For example, by calculating
  statistical properties of the light curve or matching the source
  with known databases.

- manual: this contains modules that, together, implement a manually
  set up decision tree, for classification. It also contains the
  :py:class:`~tkp.classification.manual.transient.Transient` class
  that characterizes a transient (in the context of the classification
  algorithms).

- automatic: this package is to be implemented, and could conceivably
  consists of a number of modules that either provide their own
  automated classification algorithms, or tie in into existing
  implementations of classification algorithms.
