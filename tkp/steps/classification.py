import logging
from lofar.parameterset import parameterset
from tkp.classification.manual.classifier import Classifier

logger = logging.getLogger(__name__)

def classify(transient, parset):
    logger.info("Classifying transient #%d", transient.runcatid)

    parset = parameterset(parset)
    weight_cutoff = parset.getFloat('weighting.cutoff')

    classifier = Classifier(transient)
    results = classifier.classify()
    transient.classification = {}
    for key, value in results.iteritems():
        if value > weight_cutoff:
            transient.classification[key] = value
    return transient
