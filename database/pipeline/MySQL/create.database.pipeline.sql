/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|       The Transient Key Project pipeline MySQL database           |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *|                                                                   |
 *| The Transient Key Project uses two databases, one for storing     |
 *| data temporarily in a working area called the "pipeline" database,|
 *| and the other as a permanent database for cataloguing and data    |
 *| mining purposes called the "catalog" database.                    |
 *|                                                                   |
 *| This scripts creates the TKP "pipeline" MySQL database.           |
 *| Run it on the command line as follows (any data in the database   |
 *| will be lost):                                                    |
 *| %>mysql -ulofar -pcs1 < MySQL.pipeline.database.create.sql        |
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

DROP DATABASE IF EXISTS pipeline;

/**
 * Create the "pipeline" database
 */
CREATE DATABASE pipeline;

USE pipeline;

/**
 * This table keeps track of the versions and changes
 */
CREATE TABLE versions (
  versionid INT NOT NULL AUTO_INCREMENT,
  version VARCHAR(32) NULL,
  creation_date DATE NOT NULL,
  scriptname VARCHAR(256) NULL,
  PRIMARY KEY (versionid)
) Engine=InnoDB;

INSERT INTO versions 
  (version
  ,creation_date
  ,scriptname
  ) VALUES 
  ("0.0.1"
  ,(SELECT now())
  ,"/pipe/database/MySQL.pipeline.database.create.sql"
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
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

/**
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */
CREATE TABLE datasets (
  dsid INT NOT NULL AUTO_INCREMENT,
  rerun INT NOT NULL DEFAULT '0',
  obs_id INT NOT NULL,
  res_id INT NOT NULL,
  dstype TINYINT NOT NULL,
  taustart_timestamp BIGINT NOT NULL, 
  dsinname VARCHAR(50) NOT NULL,
  dsoutname VARCHAR(50) DEFAULT NULL,
  description VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (dsid),
  INDEX (obs_id),
  FOREIGN KEY (obs_id) REFERENCES observations(obsid),
  INDEX (res_id),
  FOREIGN KEY (res_id) REFERENCES resolutions(resid),
  INDEX (taustart_timestamp)
) ENGINE=InnoDB;

/**
 * This table contains the different types
 * in our databases.
 */
CREATE TABLE classification (
  classid INT NOT NULL,
  type INT NOT NULL,
  class VARCHAR(10) DEFAULT NULL,
  description VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (classid),
  INDEX (type)
) ENGINE=InnoDB;

/**
 * This table stores the information about the catalogues that are
 * loaded into the pipeline database.
 */
CREATE TABLE catalogues (
  catid INT NOT NULL AUTO_INCREMENT,
  catname VARCHAR(50) NOT NULL,
  fullname VARCHAR(250) NOT NULL,
  PRIMARY KEY (catid)
) ENGINE=InnoDB;

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
  cat_id INT NOT NULL,
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
  UNIQUE INDEX (catsrcid),
  UNIQUE INDEX (cat_id
               ,orig_catsrcid),
  INDEX (orig_catsrcid),
  FOREIGN KEY (cat_id) REFERENCES catalogues(catid),
  INDEX (band),
  FOREIGN KEY (band) REFERENCES frequencybands(freqbandid),
  INDEX (class_id),
  FOREIGN KEY (class_id) REFERENCES classification(classid)
) ENGINE=InnoDB;

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
 * det_sigma:       The sigma level of the detection,
 *                  20*(I_peak/det_sigma) gives the rms of the detection.
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
  margin BIT NOT NULL DEFAULT 0,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  det_sigma DOUBLE NOT NULL,
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
  UNIQUE INDEX (tau
               ,band
               ,seq_nr
               ,xtrsrcid
               ),
  UNIQUE INDEX (xtrsrcid),
  INDEX (band),
  FOREIGN KEY (band) REFERENCES frequencybands(freqbandid),
  INDEX (seq_nr),
  INDEX (ds_id),
  FOREIGN KEY (ds_id) REFERENCES datasets(dsid),
  INDEX(assoc_xtrsrcid),
  INDEX(assoc_catsrcid),
  FOREIGN KEY (assoc_catsrcid) REFERENCES cataloguesources(catsrcid),
  INDEX (class_id),
  FOREIGN KEY (class_id) REFERENCES classification(classid)
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;


/**
 * ZoneZone table maps each zone to zones which may have a cross match
 */
CREATE TABLE zonezone (
  zone1 INT, 
  zone2 INT, 
  alpha DOUBLE,
  PRIMARY KEY (zone1
	      ,zone2)
) ENGINE=InnoDB;

/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|                    This section describes                         |
 *|                 the functions and procedures                      |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */

DELIMITER //

/**
 * This function computes the ra expansion for a given theta at 
 * a given declination.
 * theta and decl are both in degrees.
 */
CREATE FUNCTION alpha(theta DOUBLE, decl DOUBLE) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN
  IF ABS(decl) + theta > 89.9 THEN 
    RETURN 180;
  ELSE 
    RETURN DEGREES(ABS(ATAN(SIN(RADIANS(theta)) / SQRT(ABS(COS(RADIANS(decl - theta)) * COS(RADIANS(decl + theta))))))) ; 
  END IF ;
END;
//

CREATE FUNCTION getBand(ifreq_eff DOUBLE, ibandwidth DOUBLE) RETURNS INT
DETERMINISTIC
BEGIN
  DECLARE ofreqbandid INT DEFAULT NULL;

  SELECT CASE WHEN COUNT(*) = 0
              THEN NULL
              ELSE freqbandid
              END
    INTO ofreqbandid
    FROM frequencybands
   WHERE freq_low <= ifreq_eff
     AND freq_high >= ifreq_eff
  ;
  
  IF ofreqbandid IS NULL THEN
    INSERT INTO frequencybands
      (freq_low
      ,freq_high
      ) VALUES
      (ifreq_eff - (ibandwidth / 2)
      ,ifreq_eff + (ibandwidth / 2)
      )
    ;
    SELECT LAST_INSERT_ID() INTO ofreqbandid;
  END IF;

  RETURN ofreqbandid;

END;
//

/**
 * This procedure builds the zones and zonezone tables according to 
 * the input zoneheight and theta (both in degrees).
 * ATTENTION:
 * The zone column in the extractedsources table will NOT be modified!
 * It is best to run this before an observation, 
 * i.e. at initialisation time.
 */
CREATE PROCEDURE BuildZones(IN izoneheight DOUBLE
                           ,IN itheta DOUBLE
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
//

/**
 * This procedure is designed to associate a single input source 
 * with a source that is closest by in the tables extractedsources 
 * and/or cataloguesources. If it cannot associate a source that is
 * close enough it will insert a null value.
 * The source is compared to the sources in the previous image in the 
 * same observation run, i.e. with identical integration time (tau) 
 * and frequency band (band).
 * If one association is found the corresponding id is set.
 * If no association is found the id is left NULL and depending on the
 * case an action is taken.
 * The input variables are the source properties.
 * TODO: Also insert margin records
 */
CREATE PROCEDURE AssociateSource(IN itau INT
                                ,IN iseq_nr INT
                                ,IN ids_id INT
                                ,IN ifreq_eff DOUBLE
                                ,IN ira DOUBLE
                                ,IN idecl DOUBLE
                                ,IN ira_err DOUBLE
                                ,IN idecl_err DOUBLE
                                ,IN iI_peak DOUBLE
                                ,IN iI_peak_err DOUBLE
                                ,IN iI_int DOUBLE
                                ,IN iI_int_err DOUBLE
                                ,IN iassoc_angle DOUBLE
                                )
BEGIN

  DECLARE ix DOUBLE;
  DECLARE iy DOUBLE;
  DECLARE iz DOUBLE;
  DECLARE ixy DOUBLE;
  /* For now, we default to the wenss catalogue
  for source asscociation */
  DECLARE icat_id INT DEFAULT 1;

  DECLARE izoneheight DOUBLE;
  DECLARE itheta DOUBLE;
  DECLARE ialpha DOUBLE;

  DECLARE iassoc_xtrsrcid INT DEFAULT NULL;
  DECLARE nassoc_xtrsrcid INT DEFAULT 0;
  DECLARE iassoc_catsrcid INT DEFAULT NULL;
  DECLARE nassoc_catsrcid INT DEFAULT 0;

  DECLARE iband INT;

  DECLARE assoc_xtr BOOLEAN DEFAULT TRUE;
  DECLARE assoc_cat BOOLEAN DEFAULT TRUE;

  DECLARE found BOOLEAN DEFAULT FALSE;
  DECLARE sigma INT DEFAULT 1;
  DECLARE iclass_id INT DEFAULT 0;
  DECLARE cat_class_id INT DEFAULT 0;
  DECLARE xtr_class_id INT DEFAULT 0;

  SET ixy = COS(RADIANS(idecl));
  SET ix = ixy * COS(RADIANS(ira));
  SET iy = ixy * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));
  SET itheta = ABS(iassoc_angle);
  SET iband = getBand(ifreq_eff, 10);

  SELECT zoneheight INTO izoneheight FROM zoneheight;
  /*SELECT GREATEST(ira_err, idecl_err) INTO itheta;*/
  SET ialpha = alpha(itheta, idecl);

  /**
   * With these source association can be run on
   * catalogue or extractedsources only. The variables
   * are internal.
   */
  SET assoc_cat = TRUE;
  SET assoc_xtr = TRUE;

  IF (assoc_cat = TRUE) THEN
    /**
     * First, we will check associations in the cataloguesources table.
     * TODO: Extend it to multiple catalogues, so we have
     * just the intersection of sources.
     */
    WHILE (found = FALSE AND sigma < 4) DO
      /* We first check the number of sources within the search radius*/
      /* For the sake of simplicity the flow is split into two queries*/
      /* TODO: This should be put into one query*/
      SELECT COUNT(*)
        INTO nassoc_catsrcid
        FROM cataloguesources
       WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                      AND FLOOR((idecl + itheta)/izoneheight)
         AND ra BETWEEN ira - ialpha
                    AND ira + ialpha
         AND decl BETWEEN idecl - itheta
                      AND idecl + itheta
         AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
         AND cat_id = icat_id
      ;
      IF nassoc_catsrcid > 0 THEN
        SELECT catsrcid
          INTO iassoc_catsrcid
          FROM cataloguesources
         WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                        AND FLOOR((idecl + itheta)/izoneheight)
           AND ra BETWEEN ira - ialpha
                      AND ira + ialpha
           AND decl BETWEEN idecl - itheta
                        AND idecl + itheta
           AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
           AND cat_id = icat_id
           AND DEGREES(ACOS(ix * x + iy * y + iz * z)) = (SELECT MIN(DEGREES(ACOS(ix * x + iy * y + iz * z)))
                                                            FROM cataloguesources
                                                          WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                                                                         AND FLOOR((idecl + itheta)/izoneheight)
                                                            AND ra BETWEEN ira - ialpha
                                                                       AND ira + ialpha
                                                            AND decl BETWEEN idecl - itheta
                                                                         AND idecl + itheta
                                                            AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
                                                            AND cat_id = icat_id
                                                         )
        ;
      END IF;
      IF nassoc_catsrcid > 0 THEN
        SET found = TRUE;
      ELSE
        SET sigma = sigma + 1;
        SET itheta = sigma * itheta / (sigma - 1);
        SET ialpha = alpha(itheta, idecl);
      END IF;
    END WHILE;

    IF nassoc_catsrcid = 1 THEN
      SET cat_class_id = 1000 + 100 * (sigma - 1);
    ELSEIF nassoc_catsrcid > 1 THEN
      SET cat_class_id = 2000 + 100 * (sigma - 1);
    END IF;

    /* This can have several results, and this number depends on the 
     * number of catalogues that is loaded into the pipeline database 
     * and in which one the source is present.
     * nassoc_catsrcid = 0:
     *   No sources found in any catalogue. This means we observe the 
     *   source for the first time. Later on we check its presence in 
     *   the extractedsources table, to see if it was observed before 
     *   in this run. For now we will leave its value set to NULL.
     * nassoc_catsrcid = 1
     *   The source was found in at least one catalogue.
     *   TODO: We have to find out about the reliability.
     * nassoc_catsrcid > 1
     *   The source can not be associated yet.
     *   Is it part of a multiple system? Or something else?
     *   We have to find out whether it appears f.ex. twice in one 
     *   catalogue or once in two different catalogues.
     *   TODO: Load more catalogues and add this check
     *   For now, we have one catalogue (wenss).
     *   For now, we will set assoc_catsrcid = -1
     */
  END IF;  

  IF (assoc_xtr = TRUE) THEN
    /**
     * Secondly, we will check for associations in extractedsources 
     * itself.
     * TODO: What if we are processing the first image?
     * Therefore we will do some tests on this source, 
     * to see if it existed in the PREVIOUS image (or not).
     * In this way even sources in non-overlapping fields will get an 
     * assoc_xtrsrcid value (if it was not detected before).
     * Furthermore, this query looks for sources within the error
     * circle of the current source.
     */
    SET found = FALSE;
    SET sigma = 1;
    SET itheta = ABS(iassoc_angle);
    /*SELECT GREATEST(ira_err, idecl_err) INTO itheta;*/
    WHILE (found = FALSE AND sigma < 4) DO
      /* Analogous to catalogue case*/
      SELECT COUNT(*)
        INTO nassoc_xtrsrcid
        FROM extractedsources
       WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight) 
                      AND FLOOR((idecl + itheta)/izoneheight)
         AND ra BETWEEN ira - ialpha 
                    AND ira + ialpha
         AND decl BETWEEN idecl - itheta 
                      AND idecl + itheta
         AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
         AND ds_id = ids_id
         AND seq_nr = iseq_nr - 1
      ;
      IF nassoc_xtrsrcid > 0 THEN
        SELECT assoc_xtrsrcid
          INTO iassoc_xtrsrcid
          FROM extractedsources
         WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight) 
                        AND FLOOR((idecl + itheta)/izoneheight)
           AND ra BETWEEN ira - ialpha 
                      AND ira + ialpha
           AND decl BETWEEN idecl - itheta 
                        AND idecl + itheta
           AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
           AND ds_id = ids_id
           AND seq_nr = iseq_nr - 1
           AND DEGREES(ACOS(ix * x + iy * y + iz * z)) = (SELECT MIN(DEGREES(ACOS(ix * x + iy * y + iz * z)))
                                                            FROM extractedsources
                                                           WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                                                                          AND FLOOR((idecl + itheta)/izoneheight)
                                                             AND ra BETWEEN ira - ialpha
                                                                        AND ira + ialpha
                                                             AND decl BETWEEN idecl - itheta
                                                                          AND idecl + itheta
                                                             AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
                                                             AND ds_id = ids_id
                                                             AND seq_nr = iseq_nr - 1
                                                         )
        ;
      END IF;
      IF nassoc_xtrsrcid > 0 THEN
        SET found = TRUE;
      ELSE
        SET sigma = sigma + 1;
        SET itheta = sigma * itheta / (sigma - 1);
        SET ialpha = alpha(itheta, idecl);
      END IF;
    END WHILE;
    /**
     * This query can have several results in combination with the
     * catalogue source association.
     * (1) nassoc_catsrcid = 0 AND nassoc_xtrsrcid = 0
     *    - This source is not in any catalogue and observed 
     *      for the first time. 
     *      If might be the first image that is processed, or a new field
     *      in an observation. 
     *      In any case the source might be new, and it can be 
     *      classified as a NEW SOURCE Candidate.
     *      TODO: How will we do/trigger this?
     *      We will set assoc_catsrcid = NULL, and 
     *      assoc_xtrsrcid = xtrsrcid by UPDATE
     * (2) nassoc_catsrcid = 0 AND nassoc_xtrsrcid = 1
     *    - This source is not known in any catalog, but we observed
     *      it before in this observation run.
     *      We will set assoc_catsrcid = NULL and
     *      assoc_xtrsrcid = iassoc_xtrsrcid
     * (3) nassoc_catsrcid = 0 AND nassoc_xtrsrcid > 1
     *    - This source is not known in the catalog, and we
     *      can associate more than one source to it.
     *      What happened before if more than one association exists?
     *      TODO: What action do we take, and how do we alert?
     *      For now, we will set assoc_catsrcid = NULL and
     *      assoc_xtrsrcid in combination with class_id = 'AME' 
     *      (associated multiple sources in extractedsources)
     * (4) nassoc_catsrcid = 1 AND nassoc_xtrsrcid = 0
     *    - This source is known in the catalog, and we observe it for
     *      the first time now. We will set 
     *      assoc_catsrcid = iassoc_catsrcid and
     *      assoc_xtrsrcid = xtrsrcid by UPDATE
     * (5) nassoc_catsrcid = 1 AND nassoc_xtrsrcid = 1
     *    - This source is known in the catalog, and we observe it 
     *      again. I'll guess this is the most common case. We will 
     *      set assoc_catsrcid = iassoc_catsrcid and
     *      assoc_xtrsrcid = iassoc_xtrsrcid
     * (6) nassoc_catsrcid = 1 AND nassoc_xtrsrcid > 1
     *    - Known in catalogue. We observed it before, but it cannot 
     *      be associated uniquely. This might occur when observing
     *      with another resolution.
     *      (compare case 0,>1) We will set
     *      assoc_catsrcid = iassoc_catsrcid and assoc_xtrsrcid in 
     *      combination with class_id = 'AME' (associated multiple 
     *      sources in extracedsources)
     * (7) nassoc_catsrcid > 1 AND nassoc_xtrsrcid = 0
     *    - There can be more than one source associated with this one.
     *      We detect it for the first time in our observation run.
     *      We will set assoc_catsrcid with class_id = 'AMC' (associated
     *      multiple source in catalogue) and 
     *      assoc_xtrsrcid = xtrsrcid by UPDATE
     * (8) nassoc_catsrcid > 1 AND nassoc_xtrsrcid = 1
     *    - There can be more than one source associated with this one.
     *      We detected it before in our observation run.
     *      We will set assoc_catsrcid with class_id = 'AMC' (associated
     *      multiple source in catalogue) and 
     *      assoc_xtrsrcid = iassoc_xtrsrcid
     * (9) nassoc_catsrcid > 1 AND nassoc_xtrsrcid > 1
     *    - There can be more than one source associated with this one.
     *      We detected it before in our observation run but can not 
     *      associate it uniquely.
     *      We will set assoc_catsrcid and assoc_xtrsrcid with 
     *      class_id = 'AMCE' (associated multiple source in catalogue 
     *      and extractedsources).
     */
  END IF;

  IF nassoc_xtrsrcid = 1 THEN
    SET xtr_class_id = 10 + sigma - 1;
  ELSEIF nassoc_xtrsrcid > 1 THEN
    SET xtr_class_id = 20 + sigma - 1;
  END IF;

  SET iclass_id = cat_class_id + xtr_class_id;

  /**
   * After this, the source can be inserted
   */
  INSERT INTO extractedsources
    (tau
    ,band
    ,seq_nr
    ,ds_id
    ,zone
    ,assoc_xtrsrcid
    ,assoc_catsrcid
    ,freq_eff
    ,class_id
    ,ra
    ,decl
    ,ra_err
    ,decl_err
    ,x
    ,y
    ,z
    ,I_peak
    ,I_peak_err
    ,I_int
    ,I_int_err
    ) 
  VALUES
    (itau
    ,iband
    ,iseq_nr
    ,ids_id
    ,FLOOR(idecl/izoneheight)
    ,iassoc_xtrsrcid
    ,iassoc_catsrcid
    ,ifreq_eff
    ,iclass_id
    ,ira
    ,idecl
    ,ira_err
    ,idecl_err
    ,ix
    ,iy
    ,iz
    ,iI_peak
    ,iI_peak_err
    ,iI_int
    ,iI_int_err
    )
  ;

  /**
   * Only if iassoc_xtrsrcid was NULL, we will set it to
   * the xtrsrcid value. We have to do an update because
   * xtrsrcid is defined as AUTO_INCREMENT
   */
  UPDATE extractedsources
     SET assoc_xtrsrcid = xtrsrcid
   WHERE assoc_xtrsrcid IS NULL
  ;

END;
//

/**
 * This procedure inserts a row in the datasets table,
 * and returns the value of the id under which it is known.
 * If the dataset name (dsinname) already exists, a new row is added
 * and the rerun value is incremented by 1. If not, it is set
 * to its default value 0.
 */
CREATE PROCEDURE InsertDataset(IN idsinname VARCHAR(50)
                              ,OUT odsid INT
                              )
BEGIN

  DECLARE irerun INT DEFAULT NULL;
  DECLARE iobs_id INT DEFAULT 1;
  DECLARE ires_id INT DEFAULT 1;
  DECLARE idstype TINYINT DEFAULT 1;
  DECLARE itaustart_timestamp BIGINT;

  SET itaustart_timestamp = REPLACE(REPLACE(REPLACE(NOW(), '-', ''), ' ', ''), ':', '');

  SELECT IFNULL(MAX(rerun), -1)
    INTO irerun
    FROM datasets
   WHERE dsinname = idsinname
  ;

  SET irerun = irerun + 1;

  INSERT INTO datasets
    (rerun
    ,obs_id
    ,res_id
    ,dstype
    ,taustart_timestamp
    ,dsinname
    ) 
  VALUES
    (irerun
    ,iobs_id
    ,ires_id
    ,idstype
    ,itaustart_timestamp
    ,idsinname
    )
  ;

  SET odsid = LAST_INSERT_ID();

END;
//

/**
 * This procedure initialises specific tables in the pipeline database
 * after it has been created successfully.
 * cataloguesources:    Table gets loaded with sources that are in the 
 *                      FoV for this observation
 */
CREATE PROCEDURE InitPipeline()
BEGIN

  /* TODO: 
   * Code here the load of the cataloguesources table
   * MySQL does not allow a LOAD DATA INFILE statement in a procedure.
   * So, this has to be done from a batch file or command line
   */ 

END;
//

/**
 * This procedure initialises the pipeline database with data 
 * that is specific to an observation.
 * BuildZones:  Creates the zoneheight and zone related tables.
 * Frequencybands:  Inserts the bands that will be observed
 * Observations:    Inserts the charateristics of this observation
 * Resolutions:     Inserts the charateristics of the resolutions
 * 
 */
CREATE PROCEDURE InitObservation(IN izoneheight DOUBLE
                                ,IN itheta DOUBLE
                                )
BEGIN

  /* We build 1 degree broad zones */
  CALL BuildZones(izoneheight, itheta);

  /* For testing, we insert some tables (after deleting old data) */
  DELETE FROM classification;
  DELETE FROM frequencybands;
  DELETE FROM datasets;
  DELETE FROM resolutions;
  DELETE FROM observations;

  INSERT INTO observations 
    (obsid
    ,time_s
    ,description
    ) VALUES 
    (1
    ,20080403140303000
    ,"test images"
    )
  ;

  INSERT INTO resolutions 
    (resid
    ,major
    ,minor
    ,pa
    ) VALUES 
    (1
    ,1
    ,1
    ,1)
  ;

  INSERT INTO datasets 
    (dsid
    ,obs_id
    ,res_id
    ,dstype
    ,taustart_timestamp
    ,dsinname
    ) VALUES 
    (1
    ,1
    ,1
    ,1
    ,20080403140303000
    ,'random***'
    )
  ;

  INSERT INTO frequencybands 
    (freqbandid
    ,freq_low
    ,freq_high
    ) VALUES 
    (1
    ,30000000
    ,40000000
    )
  ;

  INSERT INTO classification 
    (classid
    ,type
    ,class
    ,description
    ) VALUES 
    ( 0, 0, 'U', 'Unknown source'),
    ( 1, 1, 'S', 'Single component source'),
    ( 2, 2, 'M', 'Multicomponent source'),
    ( 3, 3, 'C', 'Component of a multicomponent source'),
    ( 4, 4, 'E', 'Extended source (more than four components)'),
    ( 5, 5, 'U', 'Unknown'),
    ( 10, 1, 'AE1', 'Associated to extractedsource'),
    ( 11, 1, 'AE2', 'Associated to extractedsource (2sigma)'),
    ( 12, 1, 'AE3', 'Associated to extractedsource (3sigma)'),
    ( 20, 1, 'AME1', 'Associated to multiple extractedsources'),
    ( 21, 1, 'AME2', 'Associated to multiple extractedsources (2sigma)'),
    ( 22, 1, 'AME2', 'Associated to multiple extractedsources (3sigma)'),
    ( 1000, 1, 'AC1', 'Associated to catalguesource'),
    ( 1010, 1, 'AC1AE1', 'AC1 + AE1'),
    ( 1011, 1, 'AC1AE2', 'AC1 + AE2'),
    ( 1012, 1, 'AC1AE3', 'AC1 + AE3'),
    ( 1020, 1, 'AC1AME1', 'AC1 + AME1'),
    ( 1021, 1, 'AC1AME2', 'AC1 + AME2'),
    ( 1022, 1, 'AC1AME3', 'AC1 + AME3'),
    ( 1100, 1, 'AC2', 'Associated to catalguesource (2sigma)'),
    ( 1110, 1, 'AC2AE1', 'AC2 + AE1'),
    ( 1111, 1, 'AC2AE2', 'AC2 + AE2'),
    ( 1112, 1, 'AC2AE3', 'AC2 + AE3'),
    ( 1120, 1, 'AC2AME1', 'AC2 + AME1'),
    ( 1121, 1, 'AC2AME2', 'AC2 + AME2'),
    ( 1122, 1, 'AC2AME3', 'AC2 + AME3'),
    ( 1200, 1, 'AC3', 'Associated to catalguesource (3sigma)'),
    ( 1210, 1, 'AC3AE1', 'AC3 + AE1'),
    ( 1211, 1, 'AC3AE2', 'AC3 + AE2'),
    ( 1212, 1, 'AC3AE3', 'AC3 + AE3'),
    ( 1220, 1, 'AC3AME1', 'AC3 + AME1'),
    ( 1221, 1, 'AC3AME2', 'AC3 + AME2'),
    ( 1222, 1, 'AC3AME3', 'AC3 + AME3'),
    ( 2000, 1, 'AMC1', 'Associated to multiple catalguesources'),
    ( 2010, 1, 'AMC1AE1', 'AMC1 + AE1'),
    ( 2011, 1, 'AMC1AE2', 'AMC1 + AE2'),
    ( 2012, 1, 'AMC1AE3', 'AMC1 + AE3'),
    ( 2020, 1, 'AMC1AME1', 'AMC1 + AME1'),
    ( 2021, 1, 'AMC1AME2', 'AMC1 + AME2'),
    ( 2022, 1, 'AMC1AME3', 'AMC1 + AME3'),
    ( 2100, 1, 'AMC2', 'Associated to multiple catalguesources (2sigma)'),
    ( 2110, 1, 'AMC2AE1', 'AMC2 + AE1'),
    ( 2111, 1, 'AMC2AE2', 'AMC2 + AE2'),
    ( 2112, 1, 'AMC2AE3', 'AMC2 + AE3'),
    ( 2120, 1, 'AMC2AME1', 'AMC2 + AME1'),
    ( 2121, 1, 'AMC2AME2', 'AMC2 + AME2'),
    ( 2122, 1, 'AMC2AME3', 'AMC2 + AME3'),
    ( 2200, 1, 'AMC3', 'Associated to multiple catalguesources (3sigma)'),
    ( 2210, 1, 'AMC3AE1', 'AMC3 + AE1'),
    ( 2211, 1, 'AMC3AE2', 'AMC3 + AE2'),
    ( 2212, 1, 'AMC3AE3', 'AMC3 + AE3'),
    ( 2220, 1, 'AMC3AME1', 'AMC3 + AME1'), 
    ( 2221, 1, 'AMC3AME2', 'AMC3 + AME2'),
    ( 2222, 1, 'AMC3AME3', 'AMC3 + AME3')
  ;

END
//

DELIMITER ;

/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|                           THE END                                 |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */
