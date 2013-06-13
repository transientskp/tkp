import logging
from tkp.classification.manual.classifier import Classifier

logger = logging.getLogger(__name__)

def classify(transient, parset):
    logger.info("Classifying transient associated with runcat: %s and band: %s",
                transient['runcat'], transient['band'])
    classifier = Classifier(transient)
    results = classifier.classify()
    transient['classification'] = {}
    for key, value in results.iteritems():
        if value > parset['weight_cutoff']:
            transient['classification'][key] = value
    return transient
