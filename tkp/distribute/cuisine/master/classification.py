"""

.. warning:

  This recipe is deprecated and in dire need of code review. (TS 26/02/12)

This recipe tries to classify one or more transients according to their
features.

Returned is a dictionary of weights (attached to the Transient object),
where each key is the type of potential source, and the value is the
corresponding weight, ie, some form of likelihood.

A cutoff parameter designates which potential sources are ignored, ie,
source classifications  with weights that fall below this parameter are
removed.

A Transient can obtain multiple source classification which don't
necessary exclude each other. Eg, 'fast transient' and 'gamma-ray burst
prompt emission' go perfectly fine together.
The first ensures some rapid action can be taken, while the latter could
alert the right people to the transient (the GRB classification could
follow from a combination of 'fast transient' and an external trigger).

"""
from lofarpipe.support import lofaringredient
from lofar.parameterset import parameterset
from tkp.classification.manual.classifier import Classifier
from tkp.distribute.cuisine.common import TrapMaster


class classification(TrapMaster):

    inputs = {
        'parset': lofaringredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Transient search configuration parset"
        ),
        'nproc': lofaringredient.IntField(
            '--nproc',
            default=8,
            help="Maximum number of simultaneous processes per output node"),
        }
    outputs = {
        'transients': lofaringredient.ListField()
        }

    def trapstep(self):
        transients = self.inputs['args']
        parset_file = self.inputs['parset']
        for transient in transients:
            self.logger.info("Classifying transient #%d", transient.runcatid)

        parset = parameterset(parset_file)
        weight_cutoff = parset.getFloat('weighting.cutoff')

        for transient in transients:
            classifier = Classifier(transient)
            results = classifier.classify()
            transient.classification = {}
            for key, value in results.iteritems():
                if value > weight_cutoff:
                    transient.classification[key] = value
        return transients
