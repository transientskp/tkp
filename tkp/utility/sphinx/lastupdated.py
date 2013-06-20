# Sphinx extension to insert the last updated date, based on the git revision
# history, into Sphinx documentation. For example, do:
#
#   .. |last_updated| last_updated::
#
#   *This document last updated:* |last_updated|.

import subprocess
from email.utils import parsedate_tz

from docutils import nodes
from sphinx.util.compat import Directive

import datetime


def setup(app):
    app.add_config_value('lastupdated_enabled', True, True)
    app.add_directive('last_updated', LastUpdatedDirective)

class LastUpdatedDirective(Directive):
    has_content = False

    def run(self):
        env = self.state.document.settings.env
        src, line = self.state_machine.get_source_and_line()
        date = subprocess.check_output(["git", "log", "-1", "--format=%cd", src])
        #If source file is new (i.e. not in repo), git returns an empty string:
        if date != '':
            date = "%d-%d-%d" % parsedate_tz(date)[:3]
        else:
            date = datetime.date.today()
            date = "%d-%d-%d" % (date.year, date.month, date.day)
        node = nodes.Text(date)
        return [node]

