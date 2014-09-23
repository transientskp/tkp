.. _code-review:

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
