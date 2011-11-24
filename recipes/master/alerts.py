from __future__ import with_statement

"""

This recipe sends email alerts for newly found transients

It will read the email addresses from the corresponding parset; 
the parset can also contain criteria which have to be satisfied 
before the email is sent. Currently, there are two types of criteria:

- a keyword is matched with the classification. This match is 
  done for a cas-insensitive substring of the classification ('icontains'),
  so a keyword like "grb" would match "GRB prompt emission".

  Multiple keywords can be given in a list; these keywords are or-ed 
  together (so ["grb", "short"]) would match "short grb", but also
  "grb" or "short duration transient".

  A single keyword should also be given in list format.


- a position is given, with a radius. When a transient is found within 
  this position (ie, exactly within the radius), a match is found.


A log of sent emails are stored in a pickle file (note: the actual
text is not stored). This is to prevent multiple emails to be sent for
the same transient.
"""


__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2011, University of Amsterdam'
__version__ = '0.1'
__last_modification__ = '2011-11-22'


import sys
import os
import pickle
from math import sqrt, cos, sin, asin, radians
from contextlib import closing
from operator import itemgetter
import smtplib

from tkp.database.database import DataBase
import tkp.database.utils as dbutils

from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support import lofaringredient
from lofarpipe.support.parset import Parset

import tkp.config
import tkp.classification
import tkp.classification.manual
from tkp.classification.manual.classifier import Classifier
from tkp.classification.manual.utils import Position
from tkp.classification.manual.utils import DateTime
from tkp.classification.manual.transient import Transient


class alerts(BaseRecipe):

    inputs = dict(
        transients=lofaringredient.ListField(
            '--transients',
            help="List of transient objects"),
        parset=lofaringredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Python file containing classification schema"),
        logfile=lofaringredient.StringField(
            '-l', '--logfile',
            dest='logfile',
            help='Pickle file to log sent emails'),
        )

    def go(self):
        super(alerts, self).go()
        transients = self.inputs['transients']
        parset = Parset(self.inputs['parset'])
        logfile = {}
        try:
            with open(self.inputs['logfile']) as infile:
                logfile = pickle.load(infile)
        except IOError:
            pass

        people = parset.getStringVector("people")
        prefs = {}
        for person in people:
            p = {}
            try:
                p['classification'] = parset.getStringVector("%s.criterion.classification" % person)
            except RuntimeError, e:
                if str(e).startswith('Key') and str(e).endswith('unknown'):
                    pass
                else:
                    raise
            try:
                p['position'] = parset.getFloatVector("%s.criterion.position" % person)
            except RuntimeError, e:
                if str(e).startswith('Key') and str(e).endswith('unknown'):
                    pass
                else:
                    raise
            email = parset.getString("%s.email" % person)
            prefs[email] = p.copy()
        
        for transient in transients:
            for email, pref in prefs.iteritems():
                if email in logfile:
                    if transient.srcid in logfile[email]:
                        continue
                if self.check_criteria(transient, pref):
                    self.send_mail(email, transient)
                    logfile.setdefault(email, []).append(transient.srcid)

        with open(self.inputs['logfile'], 'w') as outfile:
            pickle.dump(logfile, outfile)
                    
        return 0

    def check_criteria(self, transient, pref):
        """Compare the user settable preferences and the
        transient characteristics

        Per criterion, list items are OR-ed together (eg, in the case
        of classification criteria).

        Then, the various criteria are AND-ed together.

        So, if both a positional and classification criterion are
        given, both will have to be satisfied; if one is missing, only
        the other one is enough.

        Returns True when the above results evaluate to True.
        """

        result = True

        self.logger.info("Checking criteria")
        for key, value in pref.iteritems():
            if key == 'position':
                p = transient.position
                x1 = cos(radians(p.dec)) * cos(radians(p.ra))
                y1 = cos(radians(p.dec)) * sin(radians(p.ra))
                z1 = sin(radians(p.dec))
                x2 = cos(radians(value[1])) * cos(radians(value[0]))
                y2 = cos(radians(value[1])) * sin(radians(value[0]))
                z2 = sin(radians(value[1]))
                theta = 2 * asin(0.5 * sqrt(
                    (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) + (z2-z1)*(z2-z1)))
                # errors and theta in arcseconds
                theta *= 3600.
                squared_error = p.ra_err * p.ra_err + p.dec_err * p.dec_err
                if squared_error + theta * theta > value[2] * value[2]:
                    result = False

            elif key == 'classification':
                classification_result = False
                # keys are the classifications, values are just the weights
                classifications = transient.classification.keys()
                for v in value:
                    for classification in classifications:
                        c = classification.lower().split()
                        if v.lower() in c:
                            classification_result = True
                            break
                if not classification_result:
                    result = False

        return result

    def send_mail(self, address, transient):
        """Send the recipient an email about this transient"""

        self.logger.info("sending email to %s for transient #%d",
                         address, transient.srcid)

        indent = 8 * " "
        features = ""
        catalogs = ""
        for key, value in sorted(transient.features.iteritems(),
                                 key=itemgetter(1)):
            try:
                features += "|" + indent + "%s: %.3f\n" % (key, value)
            except TypeError:  # incorrect format argument
                features += "|" + indent + "%s: %s\n" % (key, str(value))
        for key, value in sorted(transient.catalogs.iteritems(),
                                 key=itemgetter(1)):
            catalogs += "|" + indent + "%s: %s\n" % (key, str(value))
        classification = ""
        for key, value in sorted(transient.classification.iteritems(),
                                 key=itemgetter(1), reverse=True):
            classification += "|" + indent + "%s: %.1f\n" % (key, value)
        message = """\
From: webadmin.api@gmail.com\r
To: %s\r
Subject: LOFAR transient alert\r

== LOFAR transient alert ==

Transient #%d
-------------        

|   T0: %s  %s
|   position: %s
|   features:
%s
|   catalogs:
%s
|   classification:
%s
""" % (address, transient.srcid,
       transient.timezero, transient.duration,
       transient.position,
       features, catalogs,
       classification)

        session = smtplib.SMTP(tkp.config.config['alerts']['server'])
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(tkp.config.config['alerts']['login'],
                      tkp.config.config['alerts']['password'])
        session.sendmail('webadmin.api@gmail.com', address, message)
                         

if __name__ == '__main__':
    sys.exit(classification().main())
