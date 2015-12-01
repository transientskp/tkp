"""
This is a placeholder for code that uses the SQLAlchemy ORM. In contains
helper functions that should make it easier to query the database

An example how to use this is shown in an IPython notebook:

https://github.com/transientskp/notebooks/blob/master/transients.ipynb

"""

from sqlalchemy.orm import aliased
from sqlalchemy.sql import func, insert

from tkp.db.model import (Assocxtrsource, Extractedsource, Image, Newsource,
                          Runningcatalog, Varmetric)


def _last_assoc_timestamps(session, dataset):
    """
    Get the timestamps of the latest assocxtrc per runningcatalog and band.

    We can't get the assoc ID's directly, because they are unique and can't
    by put in the group by. You can get the eventual assoc ID's by joining
    this query again with the assoc table (see last_assoc_per_band func)

    args:
        session (session): A SQLAlchemy session
        dataset (Dataset): A SQLALchemy dataset model

    returns: a SQLAlchemy subquery containing  runcat id, timestamp, band id
    """
    a = aliased(Assocxtrsource, name='a_timestamps')
    e = aliased(Extractedsource, name='e_timestamps')
    r = aliased(Runningcatalog, name='r_timestamps')
    i = aliased(Image, name='i_timestamps')
    return session.query(r.id.label('runcat'),
                         func.max(i.taustart_ts).label('max_time'),
                         i.band_id.label('band')
                         ). \
        select_from(r). \
        join(a, r.id == a.runcat_id). \
        join(e, a.xtrsrc_id == e.id). \
        join(i, i.id == e.image_id). \
        group_by(r.id, i.band_id). \
        filter(i.dataset == dataset). \
        subquery(name='last_assoc_timestamps')


def _last_assoc_per_band(session, dataset):
    """
    Get the ID's of the latest assocxtrc per runningcatalog and band.

    Very similar to last_assoc_timestamps, but returns the ID's

    args:
        session: SQLalchemy session objects
        dataset: tkp.db.model.dataset object

    returns: SQLAlchemy subquery
    """
    l = _last_assoc_timestamps(session, dataset)
    a = aliased(Assocxtrsource, name='a_laids')
    e = aliased(Extractedsource, name='e_laids')
    i = aliased(Image, name='i_laids')

    return session.query(a.id.label('assoc_id'), l.c.max_time,
                         l.c.band, l.c.runcat). \
        select_from(l). \
        join(a, a.runcat_id == l.c.runcat). \
        join(e, a.xtrsrc_id == e.id). \
        join(i, (i.id == e.image_id) & (i.taustart_ts == l.c.max_time)). \
        subquery(name='last_assoc_per_band')


def _last_ts_fmax(session, dataset):
    """
    Select peak flux per runcat at last timestep (over all bands)

    args:
        session: SQLalchemy session objects
        dataset: tkp.db.model.dataset object

    returns: SQLAlchemy subquery
    """
    a = aliased(Assocxtrsource, name='a_lt')
    e = aliased(Extractedsource, name='e_lt')

    subquery = _last_assoc_per_band(session, dataset)
    return session.query(a.runcat_id.label('runcat_id'),
                         func.max(e.f_int).label('max_flux')
                         ). \
        select_from(subquery). \
        join(a, a.id == subquery.c.assoc_id). \
        join(e, a.xtrsrc_id == e.id). \
        group_by(a.runcat_id). \
        subquery(name='last_ts_fmax')


def _newsrc_trigger(session, dataset):
    """
    Grab newsource /trigger details where possible

    args:
        session: SQLalchemy session objects

    returns: SQLAlchemy subquery
    """
    newsource = aliased(Newsource, name='n_ntr')
    e = aliased(Extractedsource, name='e_ntr')
    i = aliased(Image, name='i_ntr')
    return session.query(
        newsource.id,
        newsource.runcat_id.label('rc_id'),
        (e.f_int / i.rms_min).label('sigma_rms_min'),
        (e.f_int / i.rms_max).label('sigma_rms_max')
    ). \
        select_from(newsource). \
        join(e, e.id == newsource.trigger_xtrsrc_id). \
        join(i, i.id == newsource.previous_limits_image_id). \
        filter(i.dataset == dataset). \
        subquery(name='newsrc_trigger')


def _combined(session, dataset):
    """

    args:
        session (Session): SQLAlchemy session
        runcat (Runningcatalog):  Running catalog model object
        dataset (Dataset): Dataset model object

    return: a SQLALchemy subquery
    """
    runcat = aliased(Runningcatalog, name='r')
    match_assoc = aliased(Assocxtrsource, name='match_assoc')
    match_ex = aliased(Extractedsource, name='match_ex')
    match_img = aliased(Image, name='match_img')
    agg_img = aliased(Image, name='agg_img')
    agg_assoc = aliased(Assocxtrsource, name='agg_assoc')
    agg_ex = aliased(Extractedsource, name='agg_ex')

    newsrc_trigger_query = _newsrc_trigger(session, dataset)
    last_ts_fmax_query = _last_ts_fmax(session, dataset)

    return session.query(
        runcat.id.label('runcat'),
        runcat.wm_ra.label('ra'),
        runcat.wm_decl.label('decl'),
        runcat.wm_uncertainty_ew,
        runcat.wm_uncertainty_ns,
        runcat.xtrsrc_id,
        runcat.dataset_id.label('dataset_id'),
        runcat.datapoints,
        match_assoc.v_int,
        match_assoc.eta_int,
        match_img.band_id,
        newsrc_trigger_query.c.id.label('newsource'),
        newsrc_trigger_query.c.sigma_rms_max.label('sigma_rms_max'),
        newsrc_trigger_query.c.sigma_rms_min.label('sigma_rms_min'),
        func.max(agg_ex.f_int).label('lightcurve_max'),
        func.avg(agg_ex.f_int).label('lightcurve_avg'),
        func.median(agg_ex.f_int).label('lightcurve_median')
    ). \
        select_from(last_ts_fmax_query). \
        join(match_assoc, match_assoc.runcat_id == last_ts_fmax_query.c.runcat_id). \
        join(match_ex,
             (match_assoc.xtrsrc_id == match_ex.id) &
             (match_ex.f_int == last_ts_fmax_query.c.max_flux)). \
        join(runcat, runcat.id == last_ts_fmax_query.c.runcat_id). \
        join(match_img, match_ex.image_id == match_img.id). \
        outerjoin(newsrc_trigger_query, newsrc_trigger_query.c.rc_id == runcat.id). \
        join(agg_assoc, runcat.id == agg_assoc.runcat_id). \
        join(agg_ex, agg_assoc.xtrsrc_id == agg_ex.id). \
        join(agg_img,
             (agg_ex.image_id == agg_img.id) & (agg_img.band_id == match_img.band_id)). \
        group_by(runcat.id,
                 runcat.wm_ra,
                 runcat.wm_decl,
                 runcat.wm_uncertainty_ew,
                 runcat.wm_uncertainty_ns,
                 runcat.xtrsrc_id,
                 runcat.dataset_id,
                 runcat.datapoints,
                 match_assoc.v_int,
                 match_assoc.eta_int,
                 match_img.band_id,
                 newsrc_trigger_query.c.id,
                 newsrc_trigger_query.c.sigma_rms_max,
                 newsrc_trigger_query.c.sigma_rms_min,
                 ). \
        filter(runcat.dataset == dataset). \
        subquery()


def store_varmetric(session, dataset):
    """
    Stores the augmented runningcatalog values in the varmetric table.
    args:
        session: A SQLAlchemy session
        dataset: a dataset model object

    :return: a SQLAlchemy query
    """
    fields = ['runcat', 'v_int', 'eta_int', 'band', 'newsource',
              'sigma_rms_max', 'sigma_rms_min', 'lightcurve_max',
              'lightcurve_avg', 'lightcurve_median']

    subquery = _combined(session=session, dataset=dataset)

    # only select the columns we are going to insert
    filtered = session.query(*fields).select_from(subquery)

    return insert(Varmetric).from_select(names=fields, select=filtered)


def calculate_varmetric(session, dataset, ra_range=None, decl_range=None,
               v_int_min=None, eta_int_min=None, sigma_rms_min_range=None,
               sigma_rms_max_range=None, new_src_only=False):
    """
    Calculate sigma_min, sigma_max, v_int, eta_int and the max and avg
    values for lightcurves, for all runningcatalogs

    It starts by getting the extracted source from latest image for a runcat.
    This is arbitrary, since you have multiple bands. We pick the band with the
    max integrated flux. Now we have v_int and eta_int.
    The flux is then devided by the RMS_max and RMS_min of the previous image
    (stored in newsource.previous_limits_image) to obtain sigma_max and
    sigma_min.

    args:
        dataset (Dataset): SQLAlchemy dataset object
        ra_range (tuple): 2 element tuple of ra range
        decl_range (tuple): 2 element tuple
        v_int_min (float): 2 element tuple
        eta_int_min (float): 2 element tuple
        sigma_rms_min_range (tuple): 2 element tuple
        sigma_rms_max_range (tuple): 2 element tuple
        new_src_only (bool):  New sources only

    returns: a SQLAlchemy query
    """

    subquery = _combined(session, dataset=dataset)
    query = session.query(subquery)

    if ra_range and decl_range:
        query = query.filter(subquery.c.ra.between(*ra_range) &
                             subquery.c.decl.between(*decl_range))

    if v_int_min != None:
        query = query.filter(subquery.c.v_int >= v_int_min)

    if eta_int_min != None:
        query = query.filter(subquery.c.eta_int >= eta_int_min)

    if sigma_rms_min_range:
        query = query.filter(subquery.c.sigma_rms_min.between(*sigma_rms_min_range))

    if sigma_rms_max_range:
        query = query.filter(subquery.c.sigma_rms_max.between(*sigma_rms_max_range))

    if new_src_only:
        query = query.filter(subquery.c.newsource != None)

    return query
