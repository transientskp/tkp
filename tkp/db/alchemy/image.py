import math
from datetime import datetime
from tkp.db.model import Frequencyband, Skyregion, Image, Dataset
from tkp.utility.coordinates import eq_to_cart
from sqlalchemy import func, cast
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION as Double



def get_band(session, dataset, freq_eff, freq_bw, freq_bw_max=.0):
    """
    Returns the frequency band for the given frequency parameters. Will create a new frequency band entry in the
    database if no match is found. You can limit the bandwidth of the band association with the freq_bw_max.

    args:
        session (sqlalchemy.orm.session.Session): a SQLAlchemy session object
        dataset (tkp.db.model.Dataset): the TraP dataset
        freq_eff (float): The central frequency of image to get band for
        freq_bw (float): The bandwidth of image to get band for
        freq_bw_max (float): The maximum bandwith used for band association. Not used if 0.0 (default).

    returns:
        tkp.db.model.Frequencyband: a frequency band object
    """
    
    if freq_bw_max == .0:
        bw_half = freq_bw / 2
        low = freq_eff - bw_half
        high = freq_eff + bw_half
    else:
        bw_half = freq_bw_max / 2
        low = freq_eff - bw_half
        high = freq_eff + bw_half

    w1 = high - low
    w2 = Frequencyband.freq_high - Frequencyband.freq_low
    max_ = func.greatest(high, Frequencyband.freq_high)
    min_ = func.least(low, Frequencyband.freq_low)

    band = session.query(Frequencyband).filter(
        (Frequencyband.dataset == dataset) & (max_ - min_ < w1 + w2)
    ).first()
    
    if not band:
        # no match so we create a new band
        band = Frequencyband(freq_central=freq_eff, freq_low=low, freq_high=high, dataset=dataset)
        session.add(band)

    return band


def update_skyregion_members(session, skyregion):
    """
    This function performs a simple distance-check against current members of the
    runningcatalog to find sources that should be visible in the given skyregion,
    and updates the assocskyrgn table accordingly.

    Any previous entries in assocskyrgn relating to this skyregion are
    deleted first.

    Note 1. We use the variable 'inter' to cache the extraction_radius as transformed
    onto the unit sphere, so this does not have to be recalculated for every
    comparison.

    Note 2. (To Do:) This distance check could be made more efficient by
    restricting to a range of RA values, as we do with the Dec.
    However, this optimization is complicated by the meridian wrap-around issue.
        """
    inter = 2. * math.sin(math.radians(skyregion.xtr_radius) / 2.)
    inter_sq = inter * inter

    q = """
      INSERT INTO assocskyrgn
        (
        runcat
        ,skyrgn
        ,distance_deg
        )
      SELECT rc.id as runcat
            ,sky.id as skyrgn
            ,DEGREES(2 * ASIN(SQRT( (rc.x - sky.x) * (rc.x - sky.x)
                                    + (rc.y - sky.y) * (rc.y - sky.y)
                                    + (rc.z - sky.z) * (rc.z - sky.z)
                                  ) / 2 )
                     )
        FROM skyregion sky
            ,runningcatalog rc
       WHERE sky.id = %(skyregion_id)s
         AND rc.dataset = sky.dataset
         AND rc.wm_decl BETWEEN sky.centre_decl - sky.xtr_radius
                            AND sky.centre_decl + sky.xtr_radius
         AND (  (rc.x - sky.x) * (rc.x - sky.x)
                + (rc.y - sky.y) * (rc.y - sky.y)
                + (rc.z - sky.z) * (rc.z - sky.z)
             ) < %(inter_sq)s
      ;
    """ % {'inter_sq': inter_sq, 'skyregion_id': skyregion.id}
    session.execute(q)
    return inter


def get_skyregion(session, dataset, centre_ra, centre_decl, xtr_radius):
    """
     gets an id for a skyregion, given a pair of central co-ordinates and a radius.

     If no matching skyregion is found, a new one is inserted. In this case we also trigger execution of
     `updateSkyRgnMembers` for the new skyregion - this performs a simple assocation with current members of the
     runningcatalog to find sources that should be visible in the new skyregion, and updates the assocskyrgn table
     accordingly.

     args:
        session (sqlalchemy.orm.session.Session): a SQLAlchemy session object
        dataset_id (int): the dataset ID
        centre_ra (float): center RA coordinate
        centre_decl (float): center DECL coordinate
        xtr_radius (float): The extraction radius

     returns:
        tkp.db.models.Skyregion: a SQLalchemy skyregion
     """
    skyregion = session.query(Skyregion).filter(Skyregion.dataset == dataset,
                                                Skyregion.centre_ra == centre_ra,
                                                Skyregion.centre_decl == centre_decl,
                                                Skyregion.xtr_radius == xtr_radius).one_or_none()
    if not skyregion:
        x, y, z = eq_to_cart(centre_ra, centre_decl)
        skyregion = Skyregion(dataset=dataset, centre_ra=centre_ra, centre_decl=centre_decl,
                              xtr_radius=xtr_radius, x=x, y=y, z=z)
        session.add(skyregion)
        session.flush()
        update_skyregion_members(session, skyregion)
    return skyregion


def insert_image(session, dataset, freq_eff, freq_bw, taustart_ts, tau_time, beam_smaj_pix, beam_smin_pix,
                 beam_pa_rad, deltax, deltay, url, centre_ra, centre_decl, xtr_radius, rms_qc, freq_bw_max=0.0,
                 rms_min=None, rms_max=None, detection_thresh=None, analysis_thresh=None):
    """
    Insert an image for a given dataset.

    Args:
        session (sqlalchemy.orm.session.Session): A SQLalchemy sessions
        dataset (int): ID of parent dataset.
        freq_eff: See :ref:`Image table definitions <schema-image>`.
        freq_bw: See :ref:`Image table definitions <schema-image>`.
        freq_bw_max (float): Optional override for freq_bw, not used if 0.
        taustart_ts: See :ref:`Image table definitions <schema-image>`.
        taus_time: See :ref:`Image table definitions <schema-image>`.
        beam_smaj_pix (float): Restoring beam semimajor axis length in pixels.
            (Converted to degrees before storing to database).
        beam_smin_pix (float): Restoring beam semiminor axis length in pixels.
            (Converted to degrees before storing to database).
        beam_pa_rad (float): Restoring beam parallactic angle in radians.
            (Converted to degrees before storing to database).
        deltax(float): Degrees per pixel increment in x-direction.
        deltay(float): Degrees per pixel increment in y-direction.
        centre_ra(float): Image central RA co-ord, in degrees.
        centre_decl(float): Image central Declination co-ord, in degrees.
        xtr_radius(float): Radius in degrees from field centre that will be used
            for source extraction.

    """
    # this looks a bit weird, but this simplifies backwards compatibility
    dataset_id = dataset
    dataset = session.query(Dataset).filter(Dataset.id == dataset_id).one()

    skyrgn = get_skyregion(session, dataset, centre_ra, centre_decl, xtr_radius)
    band = get_band(session, dataset, freq_eff, freq_bw, freq_bw_max)
    rb_smaj = beam_smaj_pix * math.fabs(deltax)
    rb_smin = beam_smin_pix * math.fabs(deltay)
    rb_pa = 180 * beam_pa_rad / math.pi

    args = ['dataset', 'band', 'tau_time', 'freq_eff', 'freq_bw', 'taustart_ts', 'skyrgn', 'rb_smaj', 'rb_smin',
            'rb_pa', 'deltax', 'deltay', 'url', 'rms_qc', 'rms_min', 'rms_max', 'detection_thresh', 'analysis_thresh']

    l = locals()
    kwargs = {arg: l[arg] for arg in args}
    image = Image(**kwargs)
    session.add(image)
    return image


def insert_dataset(session, description):
    rerun = session.query(func.max(Dataset.rerun)). \
        select_from(Dataset).  \
        filter(Dataset.description == "description"). \
        one()[0]

    if not rerun:
        rerun = 0
    else:
        rerun += 1

    dataset = Dataset(rerun=rerun,
                      process_start_ts=datetime.now(),
                      description=description)
    session.add(dataset)
    return dataset
