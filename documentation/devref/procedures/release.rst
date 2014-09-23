Release procedure
=================

Code and repository management
------------------------------

To make a release you should first create a new branch (if appropriate: see
below), then set the version number in the code, then tag the new release.

Major releases are sequentially numbered (``1``, ``2``, ``N``). They happen on
a branch named ``releaseN``. Create the branch as follows::

  $ git checkout -b <releaseN>

Minor releases happen on existing release branches. They are named ``N.M``,
where ``N`` is the major release version and ``M`` the minor version. The
first commit on every release branch corresponds to ``N.0``. Check
out the relevant branch::

  $ git checkout <releaseN>

Next, edit the code to set the version number. You will need to change the
following files:

  * ``setup.py``
  * ``tkp/__init__.py``
  * ``documentation/conf.py``

Commit your changes. This commit is the basis of the release::

  $ git commit -am "Release N.M"

Tag the release. This is important, as we use the tags to indicate which
versions should be built and added to the documentation site::

  $ git tag -a "rN.M"

Push everything, including the tag, to GitHub::

  $ git push --tags origin releaseN

