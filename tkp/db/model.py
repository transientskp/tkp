"""
The SQLAlchemy model definition.

revision history:

 38 - add varmetric table
 37 - add forcedfits_count column to runningcatalog
 36 - switch to SQLAlchemy schema initialisation
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index,\
    Integer, SmallInteger, String, text, Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION as Double


SCHEMA_VERSION = 38

Base = declarative_base()
metadata = Base.metadata


class Assocskyrgn(Base):
    __tablename__ = 'assocskyrgn'

    id = Column(Integer, primary_key=True)
    runcat_id = Column('runcat', ForeignKey('runningcatalog.id'), nullable=False, index=True)
    runcat = relationship('Runningcatalog')

    skyrgn_id = Column('skyrgn', ForeignKey('skyregion.id'), nullable=False, index=True)
    skyrgn = relationship('Skyregion')

    distance_deg = Column(Double)


class Assocxtrsource(Base):
    __tablename__ = 'assocxtrsource'
    __table_args__ = (
        Index('assocxtrsource_runcat_xtrsrc_key', 'runcat', 'xtrsrc',
              unique=True),
    )

    id = Column(Integer, primary_key=True)

    runcat_id = Column('runcat', ForeignKey('runningcatalog.id'), nullable=False)
    runcat = relationship('Runningcatalog')

    xtrsrc_id = Column('xtrsrc', ForeignKey('extractedsource.id'), index=True)
    xtrsrc = relationship('Extractedsource')

    type = Column(SmallInteger, nullable=False)
    distance_arcsec = Column(Double)
    r = Column(Double)
    loglr = Column(Double)
    v_int = Column(Double, nullable=False)
    eta_int = Column(Double, nullable=False)
    f_datapoints = Column(Integer, nullable=False)


class Config(Base):
    __tablename__ = 'config'
    __table_args__ = (
        Index('config_dataset_section_key_key', 'dataset', 'section', 'key',
              unique=True),
    )

    id = Column(Integer, primary_key=True)

    dataset_id = Column('dataset', ForeignKey('dataset.id'), nullable=False)
    dataset = relationship('Dataset')

    section = Column(String(100))
    key = Column(String(100))
    value = Column(String(500))
    type = Column(String(5))


seq_dataset = Sequence('seq_dataset')

class Dataset(Base):
    __tablename__ = 'dataset'

    id = Column(Integer, seq_dataset, server_default=seq_dataset.next_value(), primary_key=True)
    rerun = Column(Integer, nullable=False, server_default=text("0"))
    type = Column(SmallInteger, nullable=False, server_default=text("1"))
    process_start_ts = Column(DateTime, nullable=False)
    process_end_ts = Column(DateTime)
    detection_threshold = Column(Double)
    analysis_threshold = Column(Double)
    assoc_radius = Column(Double)
    backsize_x = Column(SmallInteger)
    backsize_y = Column(SmallInteger)
    margin_width = Column(Double)
    description = Column(String(100), nullable=False)
    node = Column(SmallInteger, nullable=False, server_default=text("1"))
    nodes = Column(SmallInteger, nullable=False, server_default=text("1"))


# extractedsource types
BLIND_FIT = 0
FORCED_FIT = 1
MONITORED_FIT = 2


class Extractedsource(Base):
    __tablename__ = 'extractedsource'

    id = Column(Integer, primary_key=True)

    image_id = Column('image', ForeignKey('image.id'), nullable=False, index=True)
    image = relationship('Image')

    ff_runcat_id = Column('ff_runcat', ForeignKey('runningcatalog.id'))
    ff_runcat = relationship('Runningcatalog',  primaryjoin='Extractedsource.ff_runcat_id == Runningcatalog.id')

    ff_monitor_id = Column('ff_monitor', ForeignKey('monitor.id'))
    ff_monitor = relationship('Monitor')

    zone = Column(Integer, nullable=False)
    ra = Column(Double, nullable=False, index=True)
    decl = Column(Double, nullable=False, index=True)
    uncertainty_ew = Column(Double, nullable=False)
    uncertainty_ns = Column(Double, nullable=False)
    ra_err = Column(Double, nullable=False, index=True)
    decl_err = Column(Double, nullable=False, index=True)
    ra_fit_err = Column(Double, nullable=False)
    decl_fit_err = Column(Double, nullable=False)
    ew_sys_err = Column(Double, nullable=False)
    ns_sys_err = Column(Double, nullable=False)
    error_radius = Column(Double, nullable=False)
    x = Column(Double, nullable=False, index=True)
    y = Column(Double, nullable=False, index=True)
    z = Column(Double, nullable=False, index=True)
    racosdecl = Column(Double, nullable=False)
    margin = Column(Boolean, nullable=False, server_default=text("false"))
    det_sigma = Column(Double, nullable=False)
    semimajor = Column(Double)
    semiminor = Column(Double)
    pa = Column(Double)
    f_peak = Column(Double)
    f_peak_err = Column(Double)
    f_int = Column(Double)
    f_int_err = Column(Double)
    chisq = Column(Double)
    reduced_chisq = Column(Double)
    extract_type = Column(SmallInteger)
    fit_type = Column(SmallInteger)

    node = Column(SmallInteger, nullable=False, server_default=text("1"))
    nodes = Column(SmallInteger, nullable=False, server_default=text("1"))


seq_frequencyband = Sequence('seq_frequencyband')


class Frequencyband(Base):
    __tablename__ = 'frequencyband'

    id = Column(Integer, seq_frequencyband, primary_key=True,
                server_default=seq_frequencyband.next_value())
    freq_central = Column(Double)
    freq_low = Column(Double)
    freq_high = Column(Double)


seq_image = Sequence('seq_image')


class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, seq_image, primary_key=True,
                server_default=seq_image.next_value())

    dataset_id = Column('dataset', Integer, ForeignKey('dataset.id'), nullable=False, index=True)
    dataset = relationship('Dataset', backref=backref('images'))

    band_id = Column('band', ForeignKey('frequencyband.id'), nullable=False, index=True)
    band = relationship('Frequencyband')

    skyrgn_id = Column('skyrgn', Integer, ForeignKey('skyregion.id'), nullable=False, index=True)
    skyrgn = relationship('Skyregion', backref=backref('images'))

    tau = Column(Integer)
    stokes = Column(SmallInteger, nullable=False, server_default=text("1"))
    tau_time = Column(Double)
    freq_eff = Column(Double, nullable=False)
    freq_bw = Column(Double)
    taustart_ts = Column(DateTime, nullable=False, index=True)
    rb_smaj = Column(Double, nullable=False)
    rb_smin = Column(Double, nullable=False)
    rb_pa = Column(Double, nullable=False)
    deltax = Column(Double, nullable=False)
    deltay = Column(Double, nullable=False)
    fwhm_arcsec = Column(Double)
    fov_degrees = Column(Double)
    rms_qc = Column(Double, nullable=False)
    rms_min = Column(Double)
    rms_max = Column(Double)
    detection_thresh = Column(Double)
    analysis_thresh = Column(Double)
    url = Column(String(1024))
    node = Column(SmallInteger, nullable=False, server_default=text("1"))
    nodes = Column(SmallInteger, nullable=False, server_default=text("1"))


class Monitor(Base):
    __tablename__ = 'monitor'

    id = Column(Integer, primary_key=True)
    dataset_id = Column('dataset', ForeignKey('dataset.id'), nullable=False, index=True)
    dataset = relationship('Dataset')

    runcat_id = Column('runcat', ForeignKey('runningcatalog.id'))
    runcat = relationship('Runningcatalog')

    ra = Column(Double, nullable=False)
    decl = Column(Double, nullable=False)
    name = Column(String(100))


class Newsource(Base):
    __tablename__ = 'newsource'

    id = Column(Integer, primary_key=True)

    runcat_id = Column('runcat', ForeignKey('runningcatalog.id'), nullable=False, index=True)
    runcat = relationship('Runningcatalog')

    trigger_xtrsrc_id = Column('trigger_xtrsrc', ForeignKey('extractedsource.id'), nullable=False, index=True)
    trigger_xtrsrc = relationship('Extractedsource')

    previous_limits_image_id = Column('previous_limits_image', ForeignKey('image.id'), nullable=False)
    previous_limits_image = relationship('Image')

    newsource_type = Column(SmallInteger, nullable=False)


class Node(Base):
    __tablename__ = 'node'
    __table_args__ = (
        Index('node_node_zone_key', 'node', 'zone', unique=True),
    )

    id = Column(Integer, primary_key=True)
    node = Column(SmallInteger, nullable=False, server_default=text("1"))
    zone = Column(SmallInteger, nullable=False)
    zone_min = Column(SmallInteger)
    zone_max = Column(SmallInteger)
    zone_min_incl = Column(Boolean, server_default=text("true"))
    zone_max_incl = Column(Boolean, server_default=text("false"))
    zoneheight = Column(Double, server_default=text("1.0"))
    nodes = Column(SmallInteger, nullable=False, server_default=text("1"))


class Rejection(Base):
    __tablename__ = 'rejection'

    id = Column(Integer, primary_key=True)

    image_id = Column('image', ForeignKey('image.id'), index=True)
    image = relationship('Image')

    # TO DO: Rename this column to 'rejectreason_id',
    # (rather than just 'rejectreason') so the model attribute matches
    # the SQL column name, avoiding the current confusing name-shadowing
    # between the SQL columns and the model attributes. (Issue #508)
    rejectreason_id = Column('rejectreason', ForeignKey('rejectreason.id'), index=True)
    rejectreason = relationship('Rejectreason')

    comment = Column(String(512))


class Rejectreason(Base):
    __tablename__ = 'rejectreason'

    id = Column(Integer,  primary_key=True)
    description = Column(String(512))


class Runningcatalog(Base):
    __tablename__ = 'runningcatalog'

    id = Column(Integer, primary_key=True)

    xtrsrc_id = Column('xtrsrc', ForeignKey('extractedsource.id'), nullable=False, unique=True)
    xtrsrc = relationship('Extractedsource', primaryjoin='Runningcatalog.xtrsrc_id == Extractedsource.id')

    dataset_id = Column('dataset', ForeignKey('dataset.id'), nullable=False, index=True)
    dataset = relationship('Dataset')

    datapoints = Column(Integer, nullable=False)
    zone = Column(Integer, nullable=False, index=True)
    wm_ra = Column(Double, nullable=False, index=True)
    wm_decl = Column(Double, nullable=False, index=True)
    wm_uncertainty_ew = Column(Double, nullable=False, index=True)
    wm_uncertainty_ns = Column(Double, nullable=False, index=True)
    avg_ra_err = Column(Double, nullable=False)
    avg_decl_err = Column(Double, nullable=False)
    avg_wra = Column(Double, nullable=False)
    avg_wdecl = Column(Double, nullable=False)
    avg_weight_ra = Column(Double, nullable=False)
    avg_weight_decl = Column(Double, nullable=False)
    x = Column(Double, nullable=False, index=True)
    y = Column(Double, nullable=False, index=True)
    z = Column(Double, nullable=False, index=True)
    inactive = Column(Boolean, nullable=False, server_default=text("false"))
    mon_src = Column(Boolean, nullable=False, server_default=text("false"))
    forcedfits_count = Column(Integer, server_default=text("0"))

    extractedsources = relationship('Extractedsource',
                                    secondary='assocxtrsource',
                                    backref='runningcatalogs')

    varmetric = relationship("Varmetric", uselist=False, backref="runcat")


class Varmetric(Base):
    __tablename__ = 'varmetric'

    id = Column(Integer, primary_key=True)

    runcat_id = Column('runcat', ForeignKey('runningcatalog.id'),
                       nullable=False, index=True)

    v_int = Column(Double, index=True)
    eta_int = Column(Double)

    band_id = Column('band', ForeignKey('frequencyband.id'), nullable=False,
                     index=True)
    band = relationship('Frequencyband')

    newsource = Column(Integer)
    sigma_rms_max = Column(Double, index=True)
    sigma_rms_min = Column(Double, index=True)
    lightcurve_max = Column(Double, index=True)
    lightcurve_avg = Column(Double, index=True)
    lightcurve_median = Column(Double, index=True)


class RunningcatalogFlux(Base):
    __tablename__ = 'runningcatalog_flux'
    __table_args__ = (
        Index('runningcatalog_flux_runcat_band_stokes_key', 'runcat', 'band',
              'stokes', unique=True),
    )

    id = Column(Integer, primary_key=True)

    runcat_id = Column('runcat', ForeignKey('runningcatalog.id'), nullable=False)
    runcat = relationship('Runningcatalog')

    band_id = Column('band', ForeignKey('frequencyband.id'), nullable=False, index=True)
    band = relationship('Frequencyband')

    stokes = Column(SmallInteger, nullable=False, server_default=text("1"))
    f_datapoints = Column(Integer, nullable=False)
    avg_f_peak = Column(Double)
    avg_f_peak_sq = Column(Double)
    avg_f_peak_weight = Column(Double)
    avg_weighted_f_peak = Column(Double)
    avg_weighted_f_peak_sq = Column(Double)
    avg_f_int = Column(Double)
    avg_f_int_sq = Column(Double)
    avg_f_int_weight = Column(Double)
    avg_weighted_f_int = Column(Double)
    avg_weighted_f_int_sq = Column(Double)


seq_skyregion = Sequence('seq_skyregion')

class Skyregion(Base):
    __tablename__ = 'skyregion'

    id = Column(Integer, seq_skyregion, primary_key=True,
                server_default=seq_skyregion.next_value())

    dataset_id = Column('dataset', ForeignKey('dataset.id'), nullable=False, index=True)
    dataset = relationship('Dataset')

    centre_ra = Column(Double, nullable=False)
    centre_decl = Column(Double, nullable=False)
    xtr_radius = Column(Double, nullable=False)
    x = Column(Double, nullable=False)
    y = Column(Double, nullable=False)
    z = Column(Double, nullable=False)


class Temprunningcatalog(Base):
    __tablename__ = 'temprunningcatalog'

    id = Column(Integer, primary_key=True)

    runcat_id = Column('runcat', ForeignKey('runningcatalog.id'), nullable=False, index=True)
    runcat = relationship('Runningcatalog')

    xtrsrc_id = Column('xtrsrc', ForeignKey('extractedsource.id'), nullable=False, index=True)
    xtrsrc = relationship('Extractedsource')

    dataset_id = Column('dataset', ForeignKey('dataset.id'), nullable=False, index=True)
    dataset = relationship('Dataset')

    band_id = Column('band', ForeignKey('frequencyband.id'), nullable=False, index=True)
    band = relationship('Frequencyband')

    distance_arcsec = Column(Double, nullable=False)
    r = Column(Double, nullable=False)
    stokes = Column(SmallInteger, nullable=False, server_default=text("1"))
    datapoints = Column(Integer, nullable=False)
    zone = Column(Integer, nullable=False)
    wm_ra = Column(Double, nullable=False)
    wm_decl = Column(Double, nullable=False)
    wm_uncertainty_ew = Column(Double, nullable=False)
    wm_uncertainty_ns = Column(Double, nullable=False)
    avg_ra_err = Column(Double, nullable=False)
    avg_decl_err = Column(Double, nullable=False)
    avg_wra = Column(Double, nullable=False)
    avg_wdecl = Column(Double, nullable=False)
    avg_weight_ra = Column(Double, nullable=False)
    avg_weight_decl = Column(Double, nullable=False)
    x = Column(Double, nullable=False)
    y = Column(Double, nullable=False)
    z = Column(Double, nullable=False)
    margin = Column(Boolean, nullable=False, server_default=text("false"))
    inactive = Column(Boolean, nullable=False, server_default=text("false"))
    beam_semimaj = Column(Double)
    beam_semimin = Column(Double)
    beam_pa = Column(Double)
    f_datapoints = Column(Integer)
    avg_f_peak = Column(Double)
    avg_f_peak_sq = Column(Double)
    avg_f_peak_weight = Column(Double)
    avg_weighted_f_peak = Column(Double)
    avg_weighted_f_peak_sq = Column(Double)
    avg_f_int = Column(Double)
    avg_f_int_sq = Column(Double)
    avg_f_int_weight = Column(Double)
    avg_weighted_f_int = Column(Double)
    avg_weighted_f_int_sq = Column(Double)


class Version(Base):
    __tablename__ = 'version'

    name = Column(String(12), primary_key=True)
    value = Column(Integer, nullable=False)
