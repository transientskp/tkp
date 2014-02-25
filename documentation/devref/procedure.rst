.. _dev-procedure:

+++++++++++++++++++++
Development Procedure
+++++++++++++++++++++

This document describes the development process used when working on the TraP.
All developers are encouraged to familiarize themselves with this material
before making any changes to the code.

Accessing the Code
==================

All code relating to the core TraP functionality is hosted in the
`transientskp/tkp <https://github.com/transientskp/tkp>`_ ``git`` repository
on `GitHub <https://github.com/>`_.

The repository is currently only available to authorized project members. If
you require access, contact ``git@transientskp.org`` for help. Please *do
not* redistribute the code without authorization.

You will need to be familiar with basic ``git`` operation before you can work
with the codebase. There are many excellent tutorials available: start at the
`Git front page <http://www.git-scm.com/>`_.

Planning
========

We aim to make releases of the TraP at the cadence of a few per year. Broadly,
the plan is to alternate technically focused releases, which clean up the
codebase and make behind-the-scenes improvements, with science based releases,
which provide new functionality to end users. Technical releases have odd
numbers; science releases even. We will provide bugfixes, but no new
development, for the most recent release; support for earlier releases is on a
"best efforts" basis only.

At the start of a release cycle, the developers and commissioners will meet to
discuss the issues which will be addressed in the upcoming release. Having
agreed upon a set of goals, a roadmap for the release will be created on the
:ref:`issue-tracker`.

It is generally acceptable to submit minor changes and tweaks, as well as
bugfixes, to the codebase at any time. However, if you are planning a major
change which will have significant repercussions for other developers, or
which causes end-user visible changes, it should be included in the goals for
a particular release and there should be a broad consensus about the plan for
implementation before you begin coding.

.. _issue-tracker:

Issue Tracker
=============

We keep track of bug reports and feature requests using the `TraP Project
<https://support.astron.nl/lofar_issuetracker/projects/bfmise>`_ on the `LOFAR
Issue Tracker <https://support.astron.nl/lofar_issuetracker/>`_. You will need
to register for the issue tracker separately with `ASTRON
<http://www.astron.nl>`_: see the `LOFAR Wiki
<http://www.lofar.org/operations/doku.php?id=maintenance:lofar_issue_tracker>`_
for details.

We use the issue tracker extensively for project planning and managing
releases. It is not a *hard* requirement that every commit to the repository
refers to a particular issue, but you are strongly encouraged to record your
activities on the tracker and to refer to it in commit messages as
appropriate.

Coding Standards
================

We do not rigorously enforce a set of coding style rules, with the sole
exception that all indents in Python code should consist of 4 spaces. However,
all code is expected to be considerately written, appropriately (but not
excessively) commented, and as easy to read as possible. Please read `PEP 8
<http://www.python.org/dev/peps/pep-0008/>`_ carefully and bear it in mind as
you work.

You may wish to run ``pylint`` or similar tools on the codebase. Occasionally,
such tools can provide useful hints about how to make your code clearer: by
all means act upon these. However, much of the output of such tools is
subjective: be sure you understand and agree with their recommendations, and
be very reluctant to apply them to pre-existing code without fully considering
the implications.

Testing
=======

Writing Tests
-------------

The TraP has a moderately-extensive (and constantly expanding!) test suite.
Whenever you make *any* changes to the code, however minor, you should check
and ensure that all the tests continue to pass. In addition, you should write
new tests to demonstrate the correctness of your changes. In particular:

* If you fix a bug, write a test which demonstrates your fix by failing before
  your code is committed, and passing afterwards;
* If you implement a new feature, write at least one test which demonstrates
  the feature in operation and shows how it behaves in likely edge cases (bad
  input, etc).

When writing new tests, follow the same organization and general style as the
existing test suite.

Running the Tests
-----------------

In order to run the test suite, you will need to download the latest revision
of the test data. This is currently stored in a `Subversion repository
<http://svn.transientskp.org/data/unittests/tkp_lib/>`_. Contact
``subversion@transientskp.org`` to request access if necessary. Download the
data to a convenient location on disk and export the ``TKP_TESTPATH``
environment variable to enable the test suite to find it.

Running the full test suite also requires that you have test :ref:`database
<database-intro>` available and initialized. Note that the schema version of
the database must match the version of the TraP you wish to test. An easy way
to configure the database such that it can be access by the test suite is to
export the environment variables ``TKP_DBENGINE``, ``TKP_DBNAME``,
``TKP_DBHOST``, ``TKP_DBPORT``, ``TKP_DBUSER`` and ``TKP_DBPASSWORD``.

You can then run the test suite by invoking ``runtests.py`` from within the
``tests`` directory in the repository.

Note that to comprehensively test the pipeline you will need to test against
*both* the ``monetdb`` and ``postgresql`` database engines.

Continuous Integration
----------------------

There is a Jenkins instance at http://jenkins.transientskp.org/ which builds
and tests the latest version of the code on the GitHub ``master`` branch.
While running the tests locally is essential, please also check Jenkins after
you have made any changes to ensure that the test suite also runs successfully
there.

Documentation
=============

Documentation is written using `Sphinx <http://www.sphinx-doc.org/>`_. The
documentation for the ``HEAD`` of the ``master`` branch of the
``transientskp/tkp`` repository is, together with the documentation for all
released versions, is automatically build every night and put online at
http://docs.transientskp.org/.

When implementing a new feature or changing the functionality or organization
of existing features, you *must* also update the documentation appropriately.

Code Review
===========

Rather than pushing changes directly to ``transientskp/tkp``, developers are
asked to submit their changes for review before they are merged into the
project. Ideally, this applies to all changes; however, it is recognized that
in certain cases -- e.g. recovering from a previous mistake, or making trivial
formatting changes -- pushing directly may be appropriate.

Code reviews are carried out using GitHub's `Pull Request
<https://help.github.com/articles/using-pull-requests>`_ functionality.

Submitting code for review
--------------------------

Using the GitHub web interface, "fork" a copy of the repository to your own
account (note that even if you do not have a paid GitHub account, forks of
private repositories remain private, so you are not exposing the code to the
outside world).

Clone a copy of your forked repository to your local system::

  $ git clone git@github.com:<username>/tkp.git

Create a branch which you will use for working on your changes::

  $ git checkout -b my_new_branch

Work on that branch, editing, adding, removing, etc as required. When you are
finished, push your changes pack to GitHub::

  $ git push orign my_new_branch

Return to the GitHub web interface, and issue a pull request to merge your
``<username>:my_new_branch`` into ``transientskp:master``.

Reviewing code
--------------

Reviewing code is just as valuable an activity as creating it: *all*
developers are expected to handle a share of code reviews. The procedure is
simple: visit the GitHub web interface, and choose a pull request to review.
Look through it carefully, ensuring that it adheres to the guidelines below.
If you are happy with it, and it can be automatically merged, simply hit the
big green "Merge Pull Request". If an automatic merge isn't possible, you will
have to check out the code onto your system and merge it manually: this takes
a little time, but GitHub document the process.

If you *aren't* happy with the code as submitted, you can use the GitHub web
interface to add both general comments covering the whole PR and to comment on
specific lines explaining what the problem is. You can even issue your own PR
suggesting new commits that the submitter could merge with their own work.
Please be as clear as possible and make constructive suggestions as to how the
submitter can make improvements: remember, the aim is to get high quality code
merged into the repository in a timely fashion, not to argue over obscure
minutiae!

Requirements for Pull Requests
------------------------------

When submitting or reviewing a pull request, please bear the following
guidelines in mind:

* PRs should be as concise and self-contained as possible. Sometimes, major
  functionality changes will require large amounts of code to be changed, but
  this should be the exception rather than the rule. Be considerate to the
  reviewer and keep changes minimal!

* It is not required that reviewers check every line for
  correctness, but they should read through the code and check that it is
  clearly structured and reasonably transparent in operation.

* Effectively all requests should be accompanied by appropriate additions to
  the test suite. If it is not possible to provide tests, the submitter should
  explain why, and the reviewer must check and agree with this justification.

* Any changes to user-visible functionality must be accompanied by appropriate
  updates to the Users' Guide.

* Any changes to APIs or the structure of code must be accompanied by
  appropriate updates to the Developers' Reference.

* Both submitter and reviewer should check that the PR does not introduce any
  regressions into the unit test results (ie, no tests which previously passed
  should fail after merging.)

* Make sure that the version control history is readable. This means both
  using descripive commit messages (future developers will not thank you for
  recording that you did "stuff"), and appropriate use of ``git rebase`` to
  eliminate dead-end and work-in-progress commits before submitting the code
  for review.

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

Local setup in Amsterdam
------------------------

All tagged releases will be build under ``/opt/tkp/[tag]``. After making &
building a release, *manually* set ``/opt/tkp/stable`` such that it is a
symlink to the latest tag.

Documentation for all tagged releases is built in ``/srv/TKP-docs/tkp/[tag]``
on ``pc-swinbank``. Edit ``/srv/TKP-docs/index.html`` such that the
documentation for every released version appears on the website.
