import logging
from collections import namedtuple

import datetime, math
import tkp.db
from tkp.db.generic import get_db_rows_as_dicts
from tkp.db.database import Database
from tkp.db.orm import DataSet, Image
from tkp.db import general as dbgen
from tkp.db import nulldetections
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
                                 'error_radius', 'fit_type',
                                 'chisq', 'reduced_chisq'
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
        query = "DELETE from newsource"
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
                                  sigma=15.,
                                  beam_maj=100., beam_min=100., beam_angle=45.,
                                  ew_sys_err=20., ns_sys_err=20.,
                                  error_radius=10.0, fit_type=0,
                                  chisq=5., reduced_chisq=1.5):
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
                                error_radius=error_radius, fit_type=fit_type,
                                chisq=chisq, reduced_chisq=reduced_chisq
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
                'f_datapoints': N
            })
    return metrics



class MockSource(object):

    def __init__(self,
                 template_extractedsource,
                 lightcurve,
                 ):
        """

        Defines a MockSource for generating mock source lists.

        (These can be used to test the database routines.)

        The lightcurve-dict entries define the times of non-zero
        flux (we do not support time-ranges here, discretely defined datapoints are
        sufficiently complex for the current unit-test suite). In this case,
        any undefined datetimes requested will produce a zero-flux measurement.
        A defaultdict may be supplied to simulate a steady-flux source.

        Args:
            template_extractedsource (ExtractedSourceTuple): This defines
                everything **except** the flux and significance of the
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
            if ex.sigma > db_image.detection_thresh:
                return ex
            else:
                return None
        else:
            raise ValueError("Unrecognised extraction type: {}".format(
                                                            extraction_type))

def insert_image_and_simulated_sources(dataset, image_params, mock_sources,
                                       new_source_sigma_margin,
                                       deruiter_radius=3.7):
    """
    Simulates the standard database image-and-source insertion logic using mock
    sources.

    Args:
        dataset: The dataset object
        image_params (dict): Contains the image properties.
        mock_sources (list of MockSource): The mock sources to simulate.
        new_source_sigma_margin (float): Parameter passed to source-association
            routines.
        deruiter_radius (float): Parameter passed to source-association
            routines.

    Returns:
        3-tuple (image, list of blind extractions, list of forced fits).

    """
    image = tkp.db.Image(data=image_params,dataset=dataset)
    blind_extractions=[]
    for src in mock_sources:
        xtr = src.simulate_extraction(image,extraction_type='blind')
        if xtr is not None:
            blind_extractions.append(xtr)
    image.insert_extracted_sources(blind_extractions,'blind')
    image.associate_extracted_sources(deRuiter_r=deruiter_radius,
        new_source_sigma_margin=new_source_sigma_margin)
    nd_ids_posns = nulldetections.get_nulldetections(image.id)
    nd_posns = [(ra,decl) for ids, ra, decl in nd_ids_posns]
    forced_fits = []
    for posn in nd_posns:
        for src in mock_sources:
            eps = 1e-13
            if (math.fabs(posn[0] - src.base_source.ra)<eps and
                        math.fabs(posn[1] - src.base_source.dec)<eps ):
                forced_fits.append(
                    src.simulate_extraction(image,extraction_type='ff_nd')
                )
    if len(nd_posns) != len(forced_fits):
        raise LookupError("Something went wrong, nulldetection position did "
                          "not match a mock source.")
    #image.insert_extracted_sources(forced_fits, 'ff_nd')
    dbgen.insert_extracted_sources(image.id, forced_fits, 'ff_nd',
                   ff_runcat_ids=[ids for ids, ra, decl in nd_ids_posns])
    nulldetections.associate_nd(image.id)

    return image, blind_extractions, forced_fits


def get_newsources_for_dataset(dsid):
    """
    Returns dicts representing all newsources for this dataset.

    Args:
        dsid: Dataset id

    Returns:
        list: (list of dicts) Each dict represents one newsource.
            The dict keys are all the columns in the newsources table, plus
            the 'taustart_ts' from the image table, which represents the
            trigger time.
    """
    qry = """\
    SELECT tr.id
          ,tr.previous_limits_image
          ,rc.id as runcat_id
          ,img.taustart_ts
          ,img.band
          ,ax.v_int
          ,ax.eta_int
          , ((ex.f_peak - limits_image.detection_thresh*limits_image.rms_min)
               / limits_image.rms_min) AS low_thresh_sigma
           , ((ex.f_peak - limits_image.detection_thresh*limits_image.rms_max)
               / limits_image.rms_max) AS high_thresh_sigma
      FROM newsource tr
          ,runningcatalog rc
          ,extractedsource ex
          ,image img
          ,assocxtrsource ax
          ,image limits_image
      WHERE rc.dataset = %(dsid)s
        AND tr.runcat = rc.id
        AND tr.trigger_xtrsrc = ex.id
        AND ex.image = img.id
        AND ax.runcat = rc.id
        AND ax.xtrsrc = ex.id
        AND tr.previous_limits_image = limits_image.id
    """
    cursor = Database().cursor
    cursor.execute(qry, {'dsid':dsid})
    newsource_rows_for_dataset = get_db_rows_as_dicts(cursor)
    return newsource_rows_for_dataset

def get_sources_filtered_by_final_variability(dataset_id,
                     eta_min,
                     v_min,
                     # minpoints
    ):
    """
    Search the database to find high-variability lightcurves.

    Uses the variability associated with the last datapoint in a lightcurve
    as the key criteria.

    Args:
        dataset_id (int): Dataset to search
        eta_min (float): Minimum value of eta-index to return.
        v_min (float): Minimum value of V-index to return.

    Returns:
        list: (list of dicts) Each dict represents a runningcatalog_flux entry
            matching the filter criteria.

    """

    query = """\
SELECT rc.id as runcat_id
      ,image.band
      ,ax.v_int
      ,ax.eta_int
FROM runningcatalog as rc
    JOIN assocxtrsource as ax ON ax.runcat = rc.id
    JOIN extractedsource as ex ON ax.xtrsrc = ex.id
    JOIN image ON ex.image = image.id
    JOIN (
        -- Determine which are the most recent variability values
        -- for each lightcurve.
        SELECT
            a.runcat as runcat_id,
            i.band as band,
            max(i.taustart_ts) as MaxTimestamp
        FROM
            assocxtrsource a
            JOIN extractedsource e ON a.xtrsrc = e.id
            JOIN image i ON e.image = i.id
        GROUP BY
            runcat_id, band
        ) last_timestamps
    ON  rc.id = last_timestamps.runcat_id
    AND image.band = last_timestamps.band
    AND image.taustart_ts = last_timestamps.MaxTimestamp
WHERE rc.dataset = %(dataset_id)s
  AND eta_int >= %(eta_min)s
  AND v_int >= %(v_min)s
"""
    cursor = tkp.db.Database().cursor
    cursor.execute(query, {'dataset_id': dataset_id,
                           'eta_min':eta_min,
                           'v_min':v_min,
                           })
    transients = get_db_rows_as_dicts(cursor)

    return transients
