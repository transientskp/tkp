import logging
from collections import namedtuple

import datetime, math
import tkp.db
from tkp.db.generic import get_db_rows_as_dicts
from tkp.db.database import Database
from tkp.db.orm import DataSet, Image
import tkp.testutil.data as testdata

import tkp.utility.coordinates as coords

ExtractedSourceTuple = namedtuple("ExtractedSourceTuple",
                                ['ra', 'dec' ,
                                 'ra_fit_err' , 'dec_fit_err' ,
                                 'peak' , 'peak_err',
                                 'flux', 'flux_err',
                                 'sigma',
                                 'beam_maj', 'beam_min', 'beam_angle',
                                 'ew_sys_err', 'ns_sys_err',
                                 'error_radius'
                                ])



def delete_test_database(database):
    """
    Use with caution!

    NB. Not the same as a freshly initialised database.
        All the sequence counters are offset.
    """
    if database.database.lower().find("test") != 0:
        raise ValueError("You tried to delete a database not prefixed with 'test'.\n"
                         "Not recommended!")
    try:
        #cursor = database.connection.cursor()
        query = "DELETE from runningcatalog_flux"
        tkp.db.execute(query, commit=True)
        query = "DELETE from assocxtrsource"
        tkp.db.execute(query, commit=True)
        query = "DELETE from assocskyrgn"
        tkp.db.execute(query, commit=True)
        query = "DELETE from temprunningcatalog"
        tkp.db.execute(query, commit=True)
        query = "DELETE from transient"
        tkp.db.execute(query, commit=True)
        query = "DELETE from runningcatalog"
        tkp.db.execute(query, commit=True)
        query = "DELETE from extractedsource"
        tkp.db.execute(query, commit=True)
        query = "DELETE from image"
        tkp.db.execute(query, commit=True)
        query = "DELETE from skyregion"
        tkp.db.execute(query, commit=True)
        query = "DELETE from dataset"
        tkp.db.execute(query, commit=True)

    except database.connection.Error:
        logging.warn("Query failed when trying to blank database\n"
                     "Query: " + query)
        raise


def example_dbimage_data_dict(**kwargs):
    """
    Defines the canonical default image-data for unit-testing the database.

    By defining this in one place we make it simple to make changes.
    A subset of the default values may be overridden by passing the keys
    as keyword-args.

    Note that while RA, Dec and extraction radius are arbitrary,
    they should (usually) be close enough and large enough to enclose
    the RA and Dec of any fake source extractions inserted, since the
    association routines reject sources outside of designated extraction
    regions.
    """
    starttime = datetime.datetime(2012, 1, 1)  # Happy new year
    time_spacing = datetime.timedelta(seconds=600)

    init_im_params = {'tau_time':300,
                      'freq_eff':140e6,
                      'freq_bw':2e6,
                      'taustart_ts':starttime,
                      'beam_smaj_pix': float(2.7),
                      'beam_smin_pix': float(2.3),
                      'beam_pa_rad': float(1.7),
                      'deltax': float(-0.01111),
                      'deltay': float(0.01111),
                      'url':testdata.fits_file,  # just an arbitrary existing fits file
                      'centre_ra': 123.,  # Arbitarily picked.
                      'centre_decl': 10.,  # Arbitarily picked.
                      'xtr_radius': 10.,  # (Degrees)
                      'rms_qc': 1.,
                      'rms_min': 1e-4, #0.1mJy RMS
                      'rms_max': 3e-4, #0.3mJy RMS
                      'detection_thresh': 6,
                      'analysis_thresh': 3
                    }
    init_im_params.update(kwargs)
    return init_im_params


def generate_timespaced_dbimages_data(n_images,
                           timedelta_between_images=datetime.timedelta(days=1),
                           **kwargs):
    """
    Generate a list of image data dictionaries.

    The image-data dicts are identical except for having the taustart_ts
    advanced by a fixed timedelta for each entry.

    These can be used to create known entries in the image table, for
    unit-testing.

    A subset of the image-data defaults may be overridden by passing the relevant
    dictionary values as keyword args.
    """
    init_im_params = example_dbimage_data_dict(**kwargs)
    im_params = []
    for i in range(n_images):
        im_params.append(init_im_params.copy())
        init_im_params['taustart_ts'] += timedelta_between_images

    return im_params


def example_extractedsource_tuple(ra=123.123, dec=10.5,  # Arbitrarily picked defaults
                                  ra_fit_err=5. / 3600, dec_fit_err=6. / 3600,
                                  peak=15e-3, peak_err=5e-4,
                                  flux=15e-3, flux_err=5e-4,
                                  sigma=15,
                                  beam_maj=100, beam_min=100, beam_angle=45,
                                  ew_sys_err=20, ns_sys_err=20,
                                  error_radius=10.0):
    """Generates an example 'fake extraction' for unit testing.

    Note that while RA and Dec are arbitrary, they should (usually) be close
    to the RA and Dec of any fake images used, since the association routines
    reject sources outside of designated extraction regions.
    """
    # NOTE: ra_fit_err & dec_fit_err are in degrees,
    # and ew_sys_err, ns_sys_err and error_radius are in arcsec.
    # The ew_uncertainty_ew is then the sqrt of the quadratic sum of the
    # systematic error and the error_radius
    return ExtractedSourceTuple(ra=ra, dec=dec,
                                ra_fit_err=ra_fit_err, dec_fit_err=dec_fit_err,
                                peak=peak, peak_err=peak_err,
                                flux=flux, flux_err=flux_err,
                                sigma=sigma,
                                beam_maj=beam_maj, beam_min=beam_min,
                                beam_angle=beam_angle,
                                ew_sys_err=ew_sys_err, ns_sys_err=ns_sys_err,
                                error_radius=error_radius
    )


def deRuiter_radius(src1, src2):
    """Calculates the De Ruiter radius for two sources"""

    # The errors are the square root of the quadratic sum of
    # the systematic and fitted errors.
    src1_ew_uncertainty = math.sqrt(src1.ew_sys_err**2 + src1.error_radius**2) / 3600.
    src1_ns_uncertainty = math.sqrt(src1.ns_sys_err**2 + src1.error_radius**2) / 3600.
    src2_ew_uncertainty = math.sqrt(src2.ew_sys_err**2 + src2.error_radius**2) / 3600.
    src2_ns_uncertainty = math.sqrt(src2.ns_sys_err**2 + src2.error_radius**2) / 3600.

    ra_nom = ((src1.ra - src2.ra) * math.cos(math.radians(0.5 * (src1.dec + src2.dec))))**2
    ra_denom = src1_ew_uncertainty**2 + src2_ew_uncertainty**2
    ra_fac = ra_nom / ra_denom

    dec_nom = (src1.dec - src2.dec)**2
    dec_denom = src1_ns_uncertainty**2 + src2_ns_uncertainty**2
    dec_fac = dec_nom / dec_denom

    dr = math.sqrt(ra_fac + dec_fac)
    return dr


def lightcurve_metrics(src_list):
    """
    Calculates various metrics for a lightcurve made up of source extractions

    These are normally calculated internally in the database - this function
    serves as a sanity check, and is used for unit-testing purposes.

    Returns a list of dictionaries, the nth dict representing the value
    of the metrics after processing the first n extractions in the lightcurve.
    The dict keys mirror the column names in the database, to make
    cross-checking of results trivial.

    Final note: this function is very inefficient, recalculating over the
    first n extractions for each step. We could make it iterative, updating
    the weighted averages as we do in the database. However, this way
    provides a stronger cross-check that our iterative SQL approaches are
    correct - less chance of making the same mistakes in two languages!

    """
    metrics = []
    for i, src in enumerate(src_list):
        N = i + 1
        avg_int_flux = sum(src.flux for src in src_list[0:N]) / N
        avg_int_flux_sq = sum(src.flux**2 for src in src_list[0:N]) / N
        avg_w_f_int = sum(src.flux/src.flux_err**2 for src in src_list[0:N]) / N
        avg_w_f_int_sq = sum(src.flux**2/src.flux_err**2 for src in src_list[0:N]) / N
        avg_w = sum(1./src.flux_err**2 for src in src_list[0:N]) / N
        if N == 1:
            v = 0.0
            eta = 0.0
        else:
            v = math.sqrt(N * (avg_int_flux_sq - avg_int_flux**2) / (N - 1.)) / avg_int_flux
            eta = N * (avg_w_f_int_sq - avg_w_f_int**2/avg_w) / (N - 1.)

        metrics.append({
                'v_int': v,
                'eta_int': eta,
                'avg_f_int': avg_int_flux,
                'avg_f_int_sq': avg_int_flux_sq,
                'avg_f_int_weight': avg_w,
                'avg_weighted_f_int': avg_w_f_int,
                'avg_weighted_f_int_sq': avg_w_f_int_sq,
            })
    return metrics



class MockSource(object):
    """Defines a MockSource for generating mock source lists.

    (These can be used to test the database routines.)

    The lightcurve-dict entries define the times of non-zero
    flux (we do not support time-ranges here, discretely defined datapoints are
    sufficiently complex for the current unit-test suite). In this case,
    any undefined datetimes requested will produce a zero-flux measurement.
    A defaultdict may be supplied to simulate a steady-flux source.
    """
    def __init__(self,
                 template_extractedsource,
                 lightcurve,
                 ):
        """
        Args:
        template_extractedsource (ExtractedSourceTuple):
            This defines everything **except** the flux and significance of the
            extraction (i.e. position, fit error, beam properties, etc.).
        lightcurve (dict): A dict mapping datetime -> flux value [Jy].
            Any undefined datetimes will produce a zero-flux measurement.
            A defaultdict with constant-valued default may be supplied to
            represent a steady source, e.g.
            >>>MockSource(base_source, defaultdict(lambda:steady_flux_val))
        """
        self.base_source = template_extractedsource
        self.lightcurve = lightcurve

    def value_at_dtime(self, dtime, image_rms):
        """Returns an `extractedsource` for a given datetime.

        If lightcurve is defined but does not contain the requested datetime,
        then peak, flux, sigma are all set to zero.
        """
        try:
            fluxval = self.lightcurve[dtime]
        except KeyError:
            fluxval = 0
        return self.base_source._replace(
                peak=fluxval,flux=fluxval,sigma=fluxval/image_rms)

    def simulate_extraction(self, db_image, extraction_type,
                            rms_attribute='rms_min'):
        """
        Simulate extraction process, returns extracted source or none.

        Uses the database image properties (extraction region, rms values)
        to determine if this source would be extracted in the given image,
        and return an extraction or None accordingly.

        Args:
            db_image (int): Database Image object.
            extraction_type: Valid values are 'blind', 'ff_nd'. If 'blind'
                then we only return an extracted source if the flux is above
                rms_value * detection_threshold.
            rms_attribute (str): Valid values are 'rms_min', 'rms_max'.
                Determines which rms value we use when deciding if this source
                will be seen in a blind extraction.

        Returns:
            ExtractedSourceTuple or None.
        """

        rms = getattr(db_image, rms_attribute)
        ex = self.value_at_dtime(db_image.taustart_ts, rms)

        #First check if source is in this image's extraction region:
        src_distance_degrees = coords.angsep(
            ex.ra, ex.dec,db_image.centre_ra, db_image.centre_decl) / 3600.0
        if src_distance_degrees > db_image.xtr_radius:
            return None

        if extraction_type == 'ff_nd':
            return ex
        elif extraction_type == 'blind':
            if ex.sigma > db_image.detection_thresh * rms:
                return ex
            else:
                return None
        else:
            raise ValueError("Unrecognised extraction type: {}".format(
                                                            extraction_type))



def get_transients_for_dataset(dsid):
    qry = """\
    SELECT tr.*
      FROM transient tr
          ,runningcatalog rc
      WHERE rc.dataset = %(dsid)s
        AND tr.runcat = rc.id
    """
    cursor = Database().connection.cursor()
    cursor.execute(qry, {'dsid':dsid})
    transient_rows_for_dataset = get_db_rows_as_dicts(cursor)
    return transient_rows_for_dataset