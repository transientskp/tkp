/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|       The Transient Key Project pipeline MonetDB database         |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *|                                                                   |
 *| The Transient Key Project uses two databases, one for storing     |
 *| data temporarily in a working area called the "pipeline" database,|
 *| and the other as a permanent database for cataloguing and data    |
 *| mining purposes called the "catalog" database.                    |
 *|                                                                   |
 *| This scripts creates the TKP "pipeline" MonetDB database.         |
 *| Run it on the command line as follows (any data in the database   |
 *| will be lost):                                                    |
 *| %>cd %/databases/MonetDB/bin                                      |
 *| %>./mclient -umonetdb -Pmonetdb -lsql < MonetDB.pipeline.database\|
 *|    .create.sql                                                    |
 *|                                                                   |
 *| A typical observation run uses the "pipeline" database as follows:|
 *| () Before observation - Initialise the database                   |
 *|     - drop the database (or recreate it)                          |
 *|     - create all the tables                                       |
 *|     - insert all the sources from the catalog database            |
 *|       that will be expected in this specific observation          |
 *|       (these include our own LOFAR catalogue as well as others)   |
 *|     - determine the height of the zones for this observation,     |
 *|       the default is 1 degree.                                    |
 *|       (it might be changed any time, but that will cost extra     |
 *|       processing time)                                            |
 *|     - call the procedure BuildZones(zoneheight, theta) to         |
 *|       fill the spatial search tables,                             |
 *|       default is "CALL BuildZones(1, 1);"                         |
 *| () During observation - Use the database                          |
 *|     - All extracted sources will be inserted into the             |
 *|       EXTRACTEDSOURCES table. Using AssociateSource() will also   |
 *|       associate them with previous inserted extracted sources and |
 *|       catalogue sources from the CATALOGUESOURCES table           |
 *|     - Transient detection                                         |
 *|       Extracted sources that can not be associated are flagged    |
 *|       as candidate transients                                     |
 *|       TODO: This is not worked out fully yet.                     |
 *| () After observation - Dump data into files                       |
 *|     - Load these data into the "catalog" database                 |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *|                         Bart Scheers                              |
 *|                          2008-03-26                               |
 *+-------------------------------------------------------------------+
 *| Open Questions:                                                   |
 *| (1) How are datasets correlated with each other?                  |
 *| (2) How do we store extended sources/emission?                    |
 *| (3) How and when do we determine the zoneheight?                  |
 *| (4) What are the predefined frequency bands?                      |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */

/**
 * Create the "pipeline" database
 */
DROP USER "lofar";

DROP SCHEMA pipeline;

CREATE USER "lofar" WITH PASSWORD 'cs1' NAME 'lofar database' SCHEMA "sys";

CREATE SCHEMA "pipeline" AUTHORIZATION "lofar";

ALTER USER "lofar" SET SCHEMA "pipeline";

SET SCHEMA "pipeline";

/**
 * This table keeps track of the versions and changes
 */
CREATE TABLE versions (
  versionid INT NOT NULL AUTO_INCREMENT,
  version VARCHAR(32) NULL,
  creation_date DATE NOT NULL,
  scriptname VARCHAR(256) NULL,
  PRIMARY KEY (versionid)
);

INSERT INTO versions 
  (version
  ,creation_date
  ,scriptname
  ) VALUES 
  ('0.0.1'
  ,(SELECT now())
  ,'/pipe/database/MonetDB.pipeline.database.create.sql'
  );

/**
 * This table contains the information about the current observation
 * time_s & _e: BIGINT is used to simulate a ms accurate timestamp
 */
CREATE TABLE observations (
  obsid INT  NOT NULL AUTO_INCREMENT,
  time_s BIGINT  NULL,
  time_e BIGINT  NULL,
  description VARCHAR(500) NULL,
  PRIMARY KEY (obsid)
);

/**
 * This table contains the information about 
 *the resolutions obtained in this observation
 */
CREATE TABLE resolutions (
  resid INT  NOT NULL,
  major DOUBLE NOT NULL,
  minor DOUBLE NOT NULL,
  pa DOUBLE NOT NULL,
  PRIMARY KEY (resid)
);

/**
 * This table contains the frequencies at which the extracted sources 
 * were detected. It might also be preloaded with the frequencies 
 * at which the stokes of the catalogue sources were measured.
 */
CREATE TABLE frequencybands (
  freqbandid INT NOT NULL AUTO_INCREMENT,
  freq_low DOUBLE DEFAULT NULL,
  freq_high DOUBLE DEFAULT NULL,
  PRIMARY KEY (freqbandid)
);

/**
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */
CREATE TABLE datasets (
  dsid INT NOT NULL,
  obs_id INT NOT NULL,
  res_id INT NOT NULL,
  dstype TINYINT NOT NULL,
  taustart_timestamp BIGINT NOT NULL, 
  dsinname CHAR(15) NOT NULL,
  dsoutname CHAR(15) DEFAULT NULL,
  desription VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (dsid),
  FOREIGN KEY (obs_id) REFERENCES observations(obsid),
  FOREIGN KEY (res_id) REFERENCES resolutions(resid)
);

/**
 * This table contains the different types
 * in our databases.
 */
CREATE TABLE classification (
  classid INT NOT NULL,
  type INT NOT NULL,
  class VARCHAR(10) DEFAULT NULL,
  description VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (classid)
);

/**
 * This table stores the information about the catalogues that are
 * loaded into the pipeline database.
 */
CREATE TABLE catalogues (
  catid TINYINT  NOT NULL AUTO_INCREMENT,
  catname VARCHAR(50) NOT NULL,
  fullname VARCHAR(250) NOT NULL,
  PRIMARY KEY (catid)
);

/**
 * This table contains the known sources that were detected previously, 
 * either by LOFAR itself or other instruments. 
 * It is a selection from the table containing all the catalogue 
 * sources (in the catlogue area). 
 * Every observation has its field(s) of view and for this all the 
 * known sources are collected. This table will be loaded from the 
 * catalogue table in the catalogue database before every observation.
 * This table will be used to load the sources table 
 * and will not be touched any more during an observation.
 * Fluxes are in Jy, ra, decl, ra_err and decl_err in degrees.
 */
CREATE TABLE cataloguesources (
  catsrcid INT NOT NULL AUTO_INCREMENT,
  orig_catsrcid INT NOT NULL,
  catsrcname VARCHAR(120) NULL,
  cat_id TINYINT NOT NULL,
  band INT NOT NULL,
  class_id INT NULL,
  zone INT NOT NULL,
  margin BOOLEAN NOT NULL DEFAULT 0,
  freq_eff DOUBLE NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  x DOUBLE NOT NULL, 
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  I_peak_avg DOUBLE NULL,
  I_peak_avg_err DOUBLE NULL,
  I_peak_min DOUBLE NULL,
  I_peak_min_err DOUBLE NULL,
  I_peak_max DOUBLE NULL,
  I_peak_max_err DOUBLE NULL,
  I_int_avg DOUBLE NULL,
  I_int_avg_err DOUBLE NULL,
  I_int_min DOUBLE NULL,
  I_int_min_err DOUBLE NULL,
  I_int_max DOUBLE NULL,
  I_int_max_err DOUBLE NULL,
  PRIMARY KEY (zone
              ,ra
              ,catsrcid),
  UNIQUE (catsrcid),
  UNIQUE (cat_id
         ,orig_catsrcid),
  FOREIGN KEY (cat_id) REFERENCES catalogues(catid),
  FOREIGN KEY (band) REFERENCES frequencybands(freqbandid),
  FOREIGN KEY (class_id) REFERENCES classification(classid)
);

/**
 * This table contains all the extracted sources during an observation.
 * To check whether a source is new, transient or variable comparisons 
 * with the cataloguesources table must be made.
 *
 * This table is empty BEFORE an observation
 * DURING an observation new sources are inserted into this table
 * AFTER an observation this table is dumped and transported to the 
 * catalogue database
 *
 * tau:             The integration time (one out of the logarithmic series)
 * band:            The frequency band (freq_eff)
 * seq_nr:          Stream of images with same tau are ordered by 
 *                  sequence number
 * ds_id:           Determines the dataset from which this source comes
 * zone:            The declination zone (decl)
 * assoc_xtrsrcid:  To which src (in this table) this xtrsrcid is associated
 * assoc_catsrcid:  To which src (in the cataloguesource table) this xtrsrcid 
 *                  is associated
 * x, y, z:         Cartesian coordinates
 * Fluxes are in Jy, ra, decl, ra_err and decl_err in degrees.
 * 
 */
CREATE TABLE extractedsources (
  tau INT NOT NULL, 
  band INT NOT NULL, 
  seq_nr INT NOT NULL, 
  xtrsrcid INT NOT NULL AUTO_INCREMENT,
  ds_id INT NOT NULL, 
  zone INT NOT NULL, 
  assoc_xtrsrcid INT NULL, 
  assoc_catsrcid INT NULL, 
  freq_eff DOUBLE NOT NULL,
  class_id INT NULL,
  margin BOOLEAN NOT NULL DEFAULT 0,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  x DOUBLE NOT NULL, 
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  I_peak DOUBLE NULL,
  Q_peak DOUBLE NULL,
  U_peak DOUBLE NULL,
  V_peak DOUBLE NULL,
  I_peak_err DOUBLE NULL,
  Q_peak_err DOUBLE NULL,
  U_peak_err DOUBLE NULL,
  V_peak_err DOUBLE NULL,
  I_int DOUBLE NULL,
  Q_int DOUBLE NULL,
  U_int DOUBLE NULL,
  V_int DOUBLE NULL,
  I_int_err DOUBLE NULL,
  Q_int_err DOUBLE NULL,
  U_int_err DOUBLE NULL,
  V_int_err DOUBLE NULL,
  PRIMARY KEY (zone
              ,ra
              ,xtrsrcid
              ),
  UNIQUE (tau
         ,band
         ,seq_nr
         ,xtrsrcid
         ),
  UNIQUE (xtrsrcid),
  FOREIGN KEY (band) REFERENCES frequencybands(freqbandid),
  FOREIGN KEY (ds_id) REFERENCES datasets(dsid),
  FOREIGN KEY (assoc_catsrcid) REFERENCES cataloguesources(catsrcid),
  FOREIGN KEY (class_id) REFERENCES classification(classid)
);

/** 
 *+--------------------------------------------------------------------+
 *|      This part creates the tables for the Zones Algorithm          |
 *+--------------------------------------------------------------------+
 *| Based on J.Gray et al. "The Zones Algorithm for Finding            |
 *| Points-Near-a-Point or Cross-Matching Spatial Datasets",           |
 *| MSR TR 2006 52, April 2006.                                        |
 *+--------------------------------------------------------------------+
 *| Create and populate the zones and zonezone tables                  |
 *| The procedure BuildZones() populates these tables.                 |
 *| zoneheight: contains zoneheight constant used by the algorithm.    |
 *|             You can update zoneheight and then call                |
 *|             BuildZones(newZoneHeight) to rebuild the indices       |
 *| zoneindex:  a table that maps type-zone-longitude to objects       |
 *|             it indexes the Place and Station table in this example.|
 *|             (This table is not used in the pipeline.)              |
 *| zones:      a table of which a row for each zone giving decl_min,  |
 *|             decl_max, Alpha                                        |
 *| zonezone:   Maps each zone to all zones it may have a cross-match  |
 *|             with.                                                  |
 *+--------------------------------------------------------------------+
 *| For now, we just use the zoneheight table. The implementation of   |
 *| zone algorithm is in the extracted- and cataloguesources tables,   |
 *| where the are in the primary key.                                  |
 *+--------------------------------------------------------------------+
 */

/**
 * Use of zoneheight drives the parameters of all the other tables.
 * Invoke BuildZones(zoneheight, theta) to change height 
 * and rebuild the indices.
 * zoneheight:  in degrees
 */
CREATE TABLE zoneheight ( 
  zoneheight DOUBLE NOT NULL
);

/**
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
);

/**
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

/**
 * This table is deprecated.
 * We will use its properties in the extractedsources and 
 * cataloguesources tables.
 */
CREATE TABLE zoneindex (
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
);


/**
 * ZoneZone table maps each zone to zones which may have a cross match
 */
CREATE TABLE zonezone (
  zone1 INT, 
  zone2 INT, 
  alpha DOUBLE,
  PRIMARY KEY (zone1
	      ,zone2)
);

/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|                    This section describes                         |
 *|                 the functions and procedures                      |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */

/**
 * These are not default in MonetDB
 */
CREATE FUNCTION degrees(r double) RETURNS double
  RETURN r*180/pi();

CREATE FUNCTION radians(d double) RETURNS double
  RETURN d*pi()/180;

/**
 * This function computes the ra expansion for a given theta at 
 * a given declination.
 * theta and decl are both in degrees.
 */
CREATE FUNCTION alpha(theta DOUBLE, decl DOUBLE) RETURNS DOUBLE 
BEGIN
  IF ABS(decl) + theta > 89.9 THEN 
    RETURN 180;
  ELSE 
    RETURN DEGREES(ABS(ATAN(SIN(RADIANS(theta)) / SQRT(ABS(COS(RADIANS(decl - theta)) * COS(RADIANS(decl + theta))))))) ; 
  END IF ;
END;

/**
 * This procedure builds the zones and zonezone tables according to 
 * the input zoneheight and theta (both in degrees).
 * ATTENTION:
 * The zone column in the extractedsources table will NOT be modified!
 * It is best to run this before an observation, 
 * i.e. at initialisation time.
 */
CREATE PROCEDURE BuildZones(izoneheight DOUBLE
                           ,itheta DOUBLE
                           )
BEGIN

  DECLARE maxZone INT;
  DECLARE minZone INT;
  DECLARE zones INT;

  DELETE FROM zoneheight;
  DELETE FROM zones;
  DELETE FROM zonezone;

  INSERT INTO zoneheight (zoneheight) VALUES (izoneheight); 

  SET maxZone = FLOOR((90.0 + izoneheight) / izoneheight);
  SET minZone = - maxZone;
  WHILE minZone < maxZone DO
    INSERT INTO zones 
    VALUES 
      (minZone
      ,minZone * izoneheight
      ,(minZone + 1) * izoneheight
      )
    ;
    SET minZone = minZone + 1;
  END WHILE;

  SET zones = CEILING(itheta/izoneheight);
  INSERT INTO zonezone
    SELECT z1.zone
          ,z2.zone
          ,CASE WHEN z1.decl_min < 0
                THEN alpha(itheta, z1.decl_min)
                ELSE alpha(itheta, z1.decl_max)
                END
      FROM zones z1 JOIN zones z2
        ON z2.zone BETWEEN z1.zone - zones AND z1.zone + zones;
END;

