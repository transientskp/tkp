"""

This recipe extracts characteristics ("features") from the variable light curve,
such as the duration, flux increase.

To do:
  - separate out the main loop over different compute nodes
  - calculate a variability measurement (use Bayesian blocks?)
  - extract non-light curve features (spectral slopes, source associations)
"""
import logging
import numpy
from tkp.database.database import Database
from tkp.classification.features import lightcurve as lcmod
from tkp.classification.features import catalogs as catmod
from tkp.database.orm import ExtractedSource

logger = logging.getLogger(__name__)

def extract_features(transient):
    database = Database()
    source = ExtractedSource(id=transient['trigger_xtrsrc'], database=database)
    # NOTE: The light curve is based on peak fluxes, while
    #       transients were found using the integrated fluxes (and errors).
    lightcurve = lcmod.LightCurve(*zip(*source.lightcurve()))
    lightcurve.calc_background()
    lightcurve.calc_stats()
    lightcurve.calc_duration()
    lightcurve.calc_fluxincrease()
    lightcurve.calc_risefall()
    if lightcurve.duration['total']:
        variability = (lightcurve.duration['active'] /
                       lightcurve.duration['total'])
    else:
        variability = numpy.NaN
    features = {
        'duration': lightcurve.duration['total'],
        'variability': variability,
        'wmean': lightcurve.stats['wmean'],
        'median': lightcurve.stats['median'],
        'wstddev': lightcurve.stats['wstddev'],
        'wskew': lightcurve.stats['wskew'],
        'wkurtosis': lightcurve.stats['wkurtosis'],
        'max': lightcurve.stats['max'],
        'peakflux': lightcurve.fluxincrease['peak'],
        'relpeakflux': lightcurve.fluxincrease['increase']['relative'],
        'risefallratio': lightcurve.risefall['ratio'],
        }

    # TODO: (gijs) a function should not modify an argument
    transient['duration'] = lightcurve.duration['total']
    transient['timezero'] = lightcurve.duration['start']
    transient['variability'] = variability
    transient['features'] = features
    transient['catalogs'] = catmod.match_catalogs(transient)

    return transient
