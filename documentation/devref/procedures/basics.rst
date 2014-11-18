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

We keep track of bug reports and feature requests using the
`Github repository issue tracker <https://github.com/transientskp/tkp/issues>`_.

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
excessively) commented, and as easy to read as possible. Please read `PEP 8`_
carefully and bear it in mind as you work.

You may wish to run ``pylint`` or similar tools on the codebase. Occasionally,
such tools can provide useful hints about how to make your code clearer: by
all means act upon these. However, much of the output of such tools is
subjective: be sure you understand and agree with their recommendations, and
be very reluctant to apply them to pre-existing code without fully considering
the implications.

.. _PEP 8: http://www.python.org/dev/peps/pep-0008/
