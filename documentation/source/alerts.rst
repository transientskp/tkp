.. _alerts:

Alerts recipe
=============
.. |last_updated| last_updated::

:author: Evert Rol
:date: |last_updated|


Introduction
------------

The alerts recipe is simple recipe ("master" only), that will send an
email alert to for new found transients to selected email
addresses. It is smart enough that it will only sent one alert per
transient per email address, to not flood people's email inboxes.


Usage
-----

Include the recipe after the classification step. Its inputs are a
parset file that sets the email addresses and criteria for sending
email alerts; a tkp.classification.manual.transient.Transient object,
which includes among other the position and classification (to be used
with the aforementioend criteria); and the filename (logfile) where
the record is kept of sent email alerts. The latter logfile is a
simple Python pickle file, similar to the state_file that keeps track
of the pipeline status.


Parset
------

The parset contains the email address to send alerts to, and can be
used to set some conditions before an email is actually sent for a
transient.

A sample parset shows this best::

    people = [p1, p2, p3]
    p1.email = person1@example.com
    p2.email = person2@example.com
    p3.email = person3@example.com
    p1.criterion.classification = [short, grb]
    p2.criterion.position = [52.70, 57.05, 10]


Person1 gets emails for transients that contain the word "short" or
"grb" in their classification. Person 2 gets emails for transients that are at
a position of RA, Dec = (52.7, 57.05), with a margin of 10 arcseconds. Person
3 will get emails for every new transient.

Note that in case of the classification, multiple keywords in a list or or-ed
together. If, however, there are multiple conditions given (such as
a classification and a position), those are and-ed together. So if Person
1 would like to receive alerts only for short grbs, the criteria would be::

    p1.criterion.classification = [short]
    p1.criterion.classification = [grb]

where as::

    p1.criterion.classification = [short, grb]

would result in receiving alerts for both short duration transients and all type
of GRBs.

If Person 1 also adds a positional criterion (eg, only short GRBs from M31),
that also gets and-ed with the other criteria: separate lines are always and-ed
together:

    p1.criterion.position = [17.1, 41.3, 7200]

If, instead, Person 1 likes to have alerts for short grbs or anything from M31,
just adds a new person:

    people = [p1, p1a, p2, p3]
    p1a.email = person1@example.com
    p1a.criterion.position = [17.1, 41.3, 7200]

Configuration
-------------

To be able to send emails, the recipe will have to connect to an email account.
For this, it will obtain the (SMTP) email details from the tkp configuration
file (:file:`${HOME}/.transientskp/tkp.cfg`); the necessary section looks
something like the following:

    [alerts]
    login = <email login>
    server = <email SMTP server>
    password = <password>
    port = <SMTP port>

Since this stores the email password in plain text, it is probably wise to
change the file permission of :file:`tkp.cfg` to 600. A future improvement may
provide support for using a local SMTP server, so that a password is not
necessary.
