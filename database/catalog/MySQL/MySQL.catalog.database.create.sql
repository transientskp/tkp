/**
 *+-------------------------------------------------------------------+
 *|                                                                   |
 *| This is the model, where we just use I1, ..., In, ..., I20        |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */
/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|       The Transient Key Project catalog MySQL database            |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *|                                                                   |
 *| The Transient Key Project pipeline uses two databases,            | 
 *| one for storing data temporarily in a working area called the     |
 *| "pipeline" database, and the other as a permanent database for    |
 *| cataloguing and data mining purposes                              |
 *| called the "catalog" database.                                    |
 *|                                                                   |
 *| This scripts creates the TKP "catalog" MySQL database.            |
 *| Run it on the command line as follows:                            |
 *| %>mysql -ulofar -pcs1 < MySQL.model.catalog.create.sql            |
 *|                                                                   |
 *| After a typical observation run the data of the "pipeline"        |
 *| database is dumped into files that are loaded into the "catalog"  |
 *| database.                                                         |
 *| () After observation - Load data                                  |
 *|     - Load data from infiles into "catalog" database              |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *|                 Bart Scheers, 2008-03-27                          |
 *+-------------------------------------------------------------------+
 */

DROP DATABASE IF EXISTS catalog;

CREATE DATABASE catalog;

USE catalog;

/**
 * This table keeps track of the versions and changes
 */
CREATE TABLE versions (
  versionid INT NOT NULL AUTO_INCREMENT,
  version VARCHAR(32) NULL,
  scriptname VARCHAR(256) NULL,
  from_msid BIGINT NULL,
  PRIMARY KEY (versionid)
) Engine=InnoDB;

INSERT INTO versions 
  (version
  ,scriptname
  ,from_msid
  ) VALUES 
  ("0.0.1"
  ,"/pipe/database/MySQL.model.catalog.create.sql"
  ,0
  )
;

CREATE TABLE classification (
  classid INT NOT NULL,
  type SMALLINT NOT NULL,
  PRIMARY KEY (classid)
) ENGINE=InnoDB;

/*
 * This table contains the information about the current observation
 * time_s & _e: BIGINT is used to simulate a ms accurate timestamp
 */
CREATE TABLE observations (
  obsid INT  NOT NULL AUTO_INCREMENT,
  time_s BIGINT  NULL,
  time_e BIGINT  NULL,
  description VARCHAR(500) NULL,
  PRIMARY KEY (obsid)
) ENGINE=InnoDB;

/*
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */
CREATE TABLE datasets (
  dsid INT NOT NULL,
  obs_id INT NOT NULL,
  dstype TINYINT NOT NULL,
  taustart_timestamp BIGINT NOT NULL, 
  dsinname CHAR(15) NOT NULL,
  dsoutname CHAR(15) DEFAULT NULL,
  desription VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (dsid),
  INDEX (obs_id),
  FOREIGN KEY (obs_id) REFERENCES observations(obsid),
  INDEX (taustart_timestamp)
) ENGINE=InnoDB;

/**
 * This table based on definitions in 
 * Helmboldt et al. (2008) ApJSS, 174:313
 * param_N:         Number of frequencies with measured flux densities
 * F74:             VLSS 74 MHz flux density
 * alpha_gt_300:    Slope of power-law fit at {nu} > 300 MHz
 * F_ext:           Extrapolated 74 MHz flux density using alp>300
 * param_A:         Equation 1 "A" parameter value (1)
 * param_B:         Equation 1 "B" parameter value (1)
 * param_C:         Equation 1 "C" parameter value (1)
 * param_D:         Equation 1 "D" parameter value (1)
 * param_rms_diff:  The rms difference between observed and 
 *                  fitted Y values (2)
 * ---------------------------------------------------------------------
 * Note (1):    Derived using a fit to the data for all sources with 
 *              Num {>=} 8; for sources where a simple linear fit gives 
 *              a quantitatively better fit (see text), 
 *              only the A and B parameters are listed.
 * Note (2):    Equal to log F_{nu}_; see equation (1) and text.
 * ---------------------------------------------------------------------
 */
CREATE TABLE spectralparameters (
  spectral_paramsid INT NOT NULL AUTO_INCREMENT,
  param_N INT NOT NULL,
  F74 DOUBLE NULL,
  alpha_gt_300 DOUBLE NULL,
  F_ext DOUBLE NULL,
  param_A DOUBLE NULL,
  param_B DOUBLE NULL,
  param_C DOUBLE NULL,
  param_D DOUBLE NULL,
  param_rms_diff DOUBLE NULL,
  PRIMARY KEY (spectral_paramsid),
  INDEX (param_N),
  INDEX (alpha_gt_300),
  INDEX (F_ext),
  INDEX (param_rms_diff)
) ENGINE=InnoDB;

/**
 * cattype:     'L': source exists in measurements
 *              'C': source exists in cataloguesources
 *              'B': source exists in both
 */
CREATE TABLE sources (
  srcid INT NOT NULL AUTO_INCREMENT,
  src_name VARCHAR(50) NULL,
  cattype CHAR(1) NULL,
  class_id INT NULL,
  zone INT NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  x DOUBLE NOT NULL,
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  spectral_params_id INT NULL,
  PRIMARY KEY (srcid),
  INDEX (src_name),
  INDEX (cattype),
  INDEX (class_id),
  FOREIGN KEY (class_id) REFERENCES classification(classid),
  INDEX (zone),
  INDEX (cattype
        ,zone
        ,ra
        ,srcid
        ),
  INDEX (cattype
        ,class_id
        ,zone
        ,ra
        ,srcid),
  FOREIGN KEY (spectral_params_id) REFERENCES spectralparameters(spectral_paramsid)
) ENGINE=InnoDB;

CREATE TABLE frequencybands (
  freqbandid INT NOT NULL,
  freqband1_low DOUBLE NULL,
  freqband1_high DOUBLE NULL,
  freqband_n_low DOUBLE NULL,
  freqband_n_high DOUBLE NULL,
  freqband20_low DOUBLE NULL,
  freqband20_high DOUBLE NULL,
  PRIMARY KEY (freqbandid)
) ENGINE=InnoDB;

CREATE TABLE effectivefrequency (
  freqeffid INT NOT NULL,
  band INT NULL,
  freq_eff1 DOUBLE NULL,
  freq_eff_n DOUBLE NULL,
  freq_eff20 DOUBLE NULL,
  PRIMARY KEY (freqeffid),
  INDEX (band),
  FOREIGN KEY (band) REFERENCES frequencybands(freqbandid)  
) ENGINE=InnoDB;

CREATE TABLE catalogues (
  catid INT NOT NULL,
  catname VARCHAR(20) NOT NULL,
  decl_min DOUBLE NULL,
  decl_max DOUBLE NULL,
  fullname VARCHAR(250) NOT NULL,
  PRIMARY KEY (catid)
) ENGINE=InnoDB;

/**
 * catsrcid:        The id
 * orig_catsrcid:   The original id of the source in the corresponding catalogue
 * src_id:          Refers to the id of the source in the sources table
 */
CREATE TABLE cataloguesources (
  catsrcid INT NOT NULL AUTO_INCREMENT,
  orig_catsrcid INT NOT NULL,
  cat_id INT NOT NULL,
  src_id INT NOT NULL,
  freqeff_id INT NOT NULL,
  I1 DOUBLE NULL,
  Q1 DOUBLE NULL,
  U1 DOUBLE NULL,
  V1 DOUBLE NULL,
  I1_int DOUBLE NULL,
  Q1_int DOUBLE NULL,
  U1_int DOUBLE NULL,
  V1_int DOUBLE NULL,
  I_n DOUBLE NULL,
  Q_n DOUBLE NULL,
  U_n DOUBLE NULL,
  V_n DOUBLE NULL,
  I_n_int DOUBLE NULL,
  Q_n_int DOUBLE NULL,
  U_n_int DOUBLE NULL,
  V_n_int DOUBLE NULL,
  I20 DOUBLE NULL,
  Q20 DOUBLE NULL,
  U20 DOUBLE NULL,
  V20 DOUBLE NULL,
  I20_int DOUBLE NULL,
  Q20_int DOUBLE NULL,
  U20_int DOUBLE NULL,
  V20_int DOUBLE NULL,
  I1_err DOUBLE NULL,
  Q1_err DOUBLE NULL,
  U1_err DOUBLE NULL,
  V1_err DOUBLE NULL,
  I1_int_err DOUBLE NULL,
  Q1_int_err DOUBLE NULL,
  U1_int_err DOUBLE NULL,
  V1_int_err DOUBLE NULL,
  I_n_err DOUBLE NULL,
  Q_n_err DOUBLE NULL,
  U_n_err DOUBLE NULL,
  V_n_err DOUBLE NULL,
  I_n_int_err DOUBLE NULL,
  Q_n_int_err DOUBLE NULL,
  U_n_int_err DOUBLE NULL,
  V_n_int_err DOUBLE NULL,
  I20_err DOUBLE NULL,
  Q20_err DOUBLE NULL,
  U20_err DOUBLE NULL,
  V20_err DOUBLE NULL,
  I20_int_err DOUBLE NULL,
  Q20_int_err DOUBLE NULL,
  U20_int_err DOUBLE NULL,
  V20_int_err DOUBLE NULL,
  PRIMARY KEY (catsrcid),
  INDEX (orig_catsrcid),
  INDEX (cat_id),
  FOREIGN KEY (cat_id) REFERENCES catalogues(catid),
  INDEX (src_id),
  FOREIGN KEY (src_id) REFERENCES sources(srcid),
  INDEX (freqeff_id),
  FOREIGN KEY (freqeff_id) REFERENCES effectivefrequency(freqeffid)
) ENGINE=InnoDB;

/**
 * TODO: We do not know what the dataset format will
 * look like. For now we adopt HDF5
 */
CREATE TABLE measurements (
  msid BIGINT NOT NULL AUTO_INCREMENT,
  src_id INT NOT NULL,
  tau INT NOT NULL,
  taustart_timestamp BIGINT NOT NULL,
  ds_id INT NOT NULL,
  freqeff_id INT NOT NULL,
  I1 DOUBLE NULL,
  Q1 DOUBLE NULL,
  U1 DOUBLE NULL,
  V1 DOUBLE NULL,
  I1_int DOUBLE NULL,
  Q1_int DOUBLE NULL,
  U1_int DOUBLE NULL,
  V1_int DOUBLE NULL,
  I_n DOUBLE NULL,
  Q_n DOUBLE NULL,
  U_n DOUBLE NULL,
  V_n DOUBLE NULL,
  I_n_int DOUBLE NULL,
  Q_n_int DOUBLE NULL,
  U_n_int DOUBLE NULL,
  V_n_int DOUBLE NULL,
  I20 DOUBLE NULL,
  Q20 DOUBLE NULL,
  U20 DOUBLE NULL,
  V20 DOUBLE NULL,
  I20_int DOUBLE NULL,
  Q20_int DOUBLE NULL,
  U20_int DOUBLE NULL,
  V20_int DOUBLE NULL,
  I1_err DOUBLE NULL,
  Q1_err DOUBLE NULL,
  U1_err DOUBLE NULL,
  V1_err DOUBLE NULL,
  I1_int_err DOUBLE NULL,
  Q1_int_err DOUBLE NULL,
  U1_int_err DOUBLE NULL,
  V1_int_err DOUBLE NULL,
  I_n_err DOUBLE NULL,
  Q_n_err DOUBLE NULL,
  U_n_err DOUBLE NULL,
  V_n_err DOUBLE NULL,
  I_n_int_err DOUBLE NULL,
  Q_n_int_err DOUBLE NULL,
  U_n_int_err DOUBLE NULL,
  V_n_int_err DOUBLE NULL,
  I20_err DOUBLE NULL,
  Q20_err DOUBLE NULL,
  U20_err DOUBLE NULL,
  V20_err DOUBLE NULL,
  I20_int_err DOUBLE NULL,
  Q20_int_err DOUBLE NULL,
  U20_int_err DOUBLE NULL,
  V20_int_err DOUBLE NULL,
  PRIMARY KEY (msid),
  INDEX (src_id),
  FOREIGN KEY (src_id) REFERENCES sources(srcid),
  INDEX (freqeff_id),
  FOREIGN KEY (freqeff_id) REFERENCES effectivefrequency(freqeffid),
  INDEX (tau),
  INDEX (taustart_timestamp),
  INDEX (ds_id),
  FOREIGN KEY (ds_id) REFERENCES datasets(dsid)
) ENGINE=InnoDB;

/** 
 *+--------------------------------------------------------------------+
 *|     This part creates the tables for the Zones Algorithm           |
 *+--------------------------------------------------------------------+
 *| J.Gray et al. "The Zones Algorithm for Finding Points-Near-a-Point |
 *| or Cross-Matching Spatial Datasets", MSR TR 2006 52, April 2006.   |
 *+--------------------------------------------------------------------+
 */

/*
 * Use a zone height drives the parameters of all the other tables.
 * Invoke BuidZoneIndex(NewZoneHeight) to change height and rebuild the indices
 * zoneheight:  in degrees
 */
CREATE TABLE zoneheight ( 
  zoneheight DOUBLE NOT NULL
) ENGINE=InnoDB;

/*
 * Zone table has a row for each zone.
 * It is used to force the query optimizer to pick the right plan
 * zone:        FLOOR(latMin/zoneHeight)', 
 * decl_min:    min declination of this zone (in degrees)', 
 * decl_max:    max declination of this zone (in degrees)', 
 */
CREATE TABLE zones (
  zone INT NOT NULL, 
  decl_min DOUBLE, 
  decl_max DOUBLE, 
  PRIMARY KEY(zone)
) ENGINE=InnoDB;

/*
 * Zone-based spatial index for Places and Stations.
 * Note the key is on objectType ('S' or 'P' for station or place in out case)
 * then zone to give the band to search in
 * then longitude to give an offset in the band.
 * then objID to give a unique key
 * It copies the spherical and cartesian coordianates from the base objects
 * it also has a flag indicating if this is a "margin" element, to solve
 * the warp-araound problem.
 * TODO: the types need still be specified
 * 	- 'C' = catalogue source
 * 	- 'X' = extracted source
 * objType: TODO: the types need still be specified
 * objid:   object Identifier in table
 * zone:    zone number (using 10 arcminutes)
 * ra,decl: sperical coordinates
 * x, y, z: cartesian coordinates
 * margin:  "margin" or "native" elements
 */

/*CREATE TABLE zoneindex (
  objType CHAR(1) NOT NULL,
  objid INT NOT NULL,
  zone INT NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  x DOUBLE NOT NULL,
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  margin BOOLEAN NOT NULL,
  PRIMARY KEY (objType
	      ,zone
	      ,ra
	      ,objid)
--  FOREIGN KEY (catsrc_id) REFERENCES cataloguesources(catsrcid)
) ENGINE=InnoDB;*/


/*
 * ZoneZone table maps each zone to zones which may have a cross match
 */
CREATE TABLE zonezone (
  zone1 INT, 
  zone2 INT, 
  alpha DOUBLE,
  PRIMARY KEY (zone1
	      ,zone2)
) ENGINE=InnoDB;

