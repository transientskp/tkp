Release procedure
=================

Code and repository management
------------------------------

We use what is sometimes known as `semantic release versioning`_.
We use branches to track major releases, and we tag all point releases,
which makes it easy to track down the relevant git history.

Versions are numbered in the format MAJOR.MINOR.PATCH,
where major releases break backwards compatibility, minor releases add
functionality without breaking backwards compatibility, and patch releases
are backwards-compatible bug fixes.

To make a release you should first create a new branch (if appropriate: see
below), then set the version number in the code, then tag the new release to
note the version number.

Major releases are sequentially numbered (``1``, ``2``, ``N``). They happen on
a branch named ``releaseN``. Create the branch as follows::

  $ git checkout -b <releaseN>

Minor releases happen on existing release branches. They are named ``N.M``,
where ``N`` is the major release version and ``M`` the minor version. The
first commit on every release branch corresponds to ``N.0.0``. Check
out the relevant branch::

  $ git checkout <releaseN>

Next, edit the code to set the version number in ``tkp/__init__.py``.

Commit your changes. This commit is the basis of the release::

  $ git commit -am "Release N.M.O"

Tag the release. This is important, as we use the tags to indicate which
versions should be built and added to the documentation site::

  $ git tag -a "rN.M.O"

Push everything, including the tag, to GitHub::

  $ git push --tags origin releaseN



.. _semantic release versioning: http://semver.org/