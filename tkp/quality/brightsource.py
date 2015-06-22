import sys
import logging
import warnings
import casacore.quanta as qa
from io import BytesIO
from casacore.measures import measures
from tkp.utility.coordinates import unix2julian
from tkp.utility.redirect_stream import redirect_stream

logger = logging.getLogger(__name__)


targets = { 'CasA': {'ra' : 6.123487680622104,  'dec' : 1.0265153995604648},
            'CygA': {'ra' : 5.233686575770755,  'dec' : 0.7109409582180791},
            'TauA': {'ra' : 1.4596748493730913, 'dec' : 0.38422502335921294},
            'HerA': {'ra' : 4.4119087330382163, 'dec' : 0.087135562905816893},
            'VirA': {'ra' : 3.276086511413598,  'dec' : 0.21626589533567378},
            'SUN': None,
            'JUPITER': None,
        }

def check_for_valid_ephemeris(measures):
    """
    Checks whether the ephemeris data in use by ``measures`` is valid.
    ``measures`` should already have a valid reference frame.
    """
    # Note that we need to catch and parse the standard error produced by
    # casacore: there doesn't seem to be any other way of figuring this out.
    casacore_stderr = BytesIO()
    with redirect_stream(sys.__stderr__, casacore_stderr):
        # We assume the ephemeris is valid if it has position of the sun.
        measures.separation(
            measures.direction("SUN"), measures.direction("SUN")
        )
    if "WARN" in casacore_stderr.getvalue():
        # casacore sends a warning to stderr if the ephemeris is invalid
        return False
    else:
        return True

def is_bright_source_near(accessor, distance=20):
    """
    Checks if there is any of the bright radio sources defined in targets
    near the center of the image.

    :param accessor: a TKP accessor
    :param distance: maximum allowed distance of a bright source (in degrees)
    :returns: False if not bright source is near, description of source if a
              bright source is near
    """

    #TODO: this function should be split up and tested more atomically
    # The measures object is our interface to casacore
    m = measures()

    # First, you need to set the reference frame -- ie, the time
    # -- used for the calculations to come. Time as MJD in seconds.
    starttime = int(accessor.taustart_ts.strftime("%s"))
    starttime_mjd = unix2julian(starttime)
    m.do_frame(m.epoch("UTC", "%ss" % starttime_mjd))

    # Now check and ensure the ephemeris in use is actually valid for this
    # data.
    if not check_for_valid_ephemeris(m):
        logger.warn("Bright source check failed due to invalid ephemeris")
        return "Invalid ephemeris"

    # Second, you need to set your image pointing.
    pointing = m.direction(
        "J2000", "%sdeg" % accessor.centre_ra,  "%sdeg"  % accessor.centre_decl
    )

    for name, position in targets.items():
        if not position:
            direction = m.direction(name)
        else:
            direction = m.direction(
                "J2000", "%srad" % position['ra'], "%srad" % position['dec']
            )
        separation = m.separation(pointing, direction).get_value("deg")
        if separation < distance:
            return "Pointing is %s degrees from %s." % (separation, name)
    return False
