import os
import logging
from lofar.parameterset import parameterset

logger = logging.getLogger(__name__)

def classify(transient, parset, tkpconfigdir=None):

    paths = [os.path.expanduser('~/.transientskp')]
    if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
        os.environ['TKPCONFIGDIR'] = tkpconfigdir
        paths.insert(0, tkpconfigdir)
    from tkp.classification.manual.classifier import Classifier

    parset = parameterset(parset)
    weight_cutoff = parset.getFloat('weighting.cutoff')

    logger.info("Classifying transient #%d", transient.runcatid)
    classifier = Classifier(transient, paths=paths)
    results = classifier.classify()
    transient.classification = {}
    for key, value in results.iteritems():
        if value > weight_cutoff:
            transient.classification[key] = value
    return transient
