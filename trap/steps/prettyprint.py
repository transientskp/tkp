"""
Pretty print the classified transients

"""

from operator import itemgetter
import logging

logger = logging.getLogger(__name__)

def prettyprint(transients):
    results = "\n====== Results ======\n"
    for transient in transients:
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
        results += """\
    \033[36m
    | transient #%d (dataset %s):
    |   T0: %s  %s
    |   position: %s
    |   features:
    %s
    |   catalogs:
    %s
    |   classification:
    %s
    \033[0m
    """ % (transient.runcatid, transient.dataset,
           transient.timezero, transient.duration,
           transient.position,
           features, catalogs,
           classification)

    results += "\n--------------------\n"
    logger.info(results)