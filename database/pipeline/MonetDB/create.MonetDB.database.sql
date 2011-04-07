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
DROP USER lofar;

DROP SCHEMA pipeline;

CREATE USER "lofar" WITH PASSWORD 'cs1' NAME 'lofar database' SCHEMA "sys";

CREATE SCHEMA "pipeline" AUTHORIZATION "lofar";

ALTER USER "lofar" SET SCHEMA "pipeline";

SET SCHEMA pipeline;

/**
 * This table keeps track of the versions and changes
 */
CREATE SEQUENCE "seq_versions" AS INTEGER;

CREATE TABLE versions (
  versionid INT NOT NULL DEFAULT NEXT VALUE FOR seq_versions,
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
  ,'/pipe/database/pipeline/MonetDB/create.database.sql'
  );

/**
 * This table contains the information about the current observation
 * time_s & _e: BIGINT is used to simulate a ms accurate timestamp
 */
CREATE SEQUENCE "seq_observations" AS INTEGER;

CREATE TABLE observations (
  obsid INT NOT NULL DEFAULT NEXT VALUE FOR seq_observations,
  time_s BIGINT NULL,
  time_e BIGINT NULL,
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
CREATE SEQUENCE "seq_frequencybands" AS INTEGER;

CREATE TABLE frequencybands (
  freqbandid INT NOT NULL DEFAULT NEXT VALUE FOR seq_frequencybands,
  freq_low DOUBLE DEFAULT NULL,
  freq_high DOUBLE DEFAULT NULL,
  PRIMARY KEY (freqbandid)
);

/**
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */
CREATE SEQUENCE "seq_datasets" AS INTEGER;

CREATE TABLE datasets (
  dsid INT NOT NULL DEFAULT NEXT VALUE FOR seq_datasets,
  rerun INT NOT NULL DEFAULT '0',
  obs_id INT NOT NULL,
  res_id INT NOT NULL,
  dstype TINYINT NOT NULL,
  taustart_timestamp BIGINT NOT NULL, 
  dsinname VARCHAR(50) NOT NULL,
  dsoutname CHAR(15) DEFAULT NULL,
  description VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (dsid),
  FOREIGN KEY (obs_id) REFERENCES observations(obsid),
  FOREIGN KEY (res_id) REFERENCES resolutions(resid)
);

/**
 * This table is deprecated. Use associations in stead.
 */
CREATE TABLE classification (
  classid INT NOT NULL,
  type INT NOT NULL,
  class VARCHAR(10) DEFAULT NULL,
  description VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (classid)
);

/**
 * This table contains the different types
 * of associations that could me made.
 */
CREATE TABLE associations (
  associd INT NOT NULL,
  type INT NOT NULL,
  assoc VARCHAR(10) DEFAULT NULL,
  description VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (associd)
);

/**
 * This table stores the information about the catalogues that are
 * loaded into the pipeline database.
 */
CREATE SEQUENCE "seq_catalogues" AS INTEGER;

CREATE TABLE catalogues (
  catid INT NOT NULL DEFAULT NEXT VALUE FOR seq_catalogues,
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
CREATE SEQUENCE "seq_cataloguesources" AS INTEGER;

CREATE TABLE cataloguesources (
  catsrcid INT NOT NULL DEFAULT NEXT VALUE FOR seq_cataloguesources,
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
CREATE SEQUENCE "seq_extractedsources" AS INTEGER;

CREATE TABLE extractedsources (
  tau INT NOT NULL, 
  band INT NOT NULL, 
  seq_nr INT NOT NULL, 
  xtrsrcid INT NOT NULL DEFAULT NEXT VALUE FOR seq_extractedsources,
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
	          ,zone2
              )
);

/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|                    This section describes                         |
 *|                 the functions and procedures                      |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *| The analogue of MySQL's LAST_INSERT_ID() is not straightforward.  |
 *| We have to execute SELECT NEXT VALUE FOR seq_tablename to get the |
 *| next id.                                                          |
 *+-------------------------------------------------------------------+
 *| Bart Scheers 2008-08-08                                           |
 *+-------------------------------------------------------------------+
 */

/**
 * These are not default in MonetDB
 */
CREATE FUNCTION degrees(r double) RETURNS double
  RETURN r * 180 / pi();

CREATE FUNCTION radians(d double) RETURNS double
  RETURN d * pi() / 180;

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
    RETURN degrees(ABS(ATAN(SIN(radians(theta)) / SQRT(ABS(COS(radians(decl - theta)) * COS(radians(decl + theta))))))) ; 
  END IF ;
END;

/**
 * Function to get the band in which this frequency belongs to.
 * If none is found, a new entry will be made
 */
CREATE FUNCTION getBand(ifreq_eff DOUBLE, ibandwidth DOUBLE) RETURNS INT
BEGIN
  DECLARE ifreqbandid INT;
  DECLARE ofreqbandid INT;
  SELECT NULL 
    INTO ofreqbandid
  ;

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
    SELECT NEXT VALUE FOR seq_frequencybands INTO ifreqbandid;
    INSERT INTO frequencybands
      (freqbandid
      ,freq_low
      ,freq_high
      ) VALUES
      (ifreqbandid
      ,ifreq_eff - (ibandwidth / 2)
      ,ifreq_eff + (ibandwidth / 2)
      )
    ;
    SET ofreqbandid = ifreqbandid;
  END IF;

  RETURN ofreqbandid;
    
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

  /* This needs to be commented, MonetDB does not insert data
   * at init
   */
  /*DELETE FROM zoneheight;
  DELETE FROM zones;
  DELETE FROM zonezone;*/

  INSERT INTO zoneheight (zoneheight) VALUES (izoneheight); 

  SET maxZone = CAST(FLOOR((90.0 + izoneheight) / izoneheight) AS INTEGER);
  SET minZone = - maxZone;
  WHILE minZone < maxZone DO
    INSERT INTO zones 
      (zone
      ,decl_min
      ,decl_max
      )
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
CREATE PROCEDURE AssociateSource(itau INT
                                ,iseq_nr INT
                                ,ids_id INT
                                ,ifreq_eff DOUBLE
                                ,ira DOUBLE
                                ,idecl DOUBLE
                                ,ira_err DOUBLE
                                ,idecl_err DOUBLE
                                ,iI_peak DOUBLE
                                ,iI_peak_err DOUBLE
                                ,iI_int DOUBLE
                                ,iI_int_err DOUBLE
                                ,iassoc_angle DOUBLE
                                )
BEGIN

  DECLARE ix DOUBLE;
  DECLARE iy DOUBLE;
  DECLARE iz DOUBLE;
  DECLARE ixy DOUBLE;
  /* For now, we default to the wenss catalogue
  for source asscociation */
  DECLARE icat_id INT;
  SELECT 1 INTO icat_id;

  DECLARE izoneheight DOUBLE;
  DECLARE itheta DOUBLE;
  DECLARE ialpha DOUBLE;

  DECLARE iassoc_xtrsrcid INT;
  DECLARE nassoc_xtrsrcid INT;
  DECLARE iassoc_catsrcid INT;
  DECLARE nassoc_catsrcid INT;
  SELECT NULL
        ,NULL 
    INTO iassoc_xtrsrcid
        ,iassoc_catsrcid
  ;

  DECLARE iband INT;

  DECLARE assoc_xtr BOOLEAN;
  DECLARE assoc_cat BOOLEAN;
  SELECT 1
        ,1
    INTO assoc_xtr
        ,assoc_cat
  ;

  DECLARE found BOOLEAN;
  DECLARE sigma INT;
  DECLARE iclass_id INT;
  DECLARE cat_class_id INT;
  DECLARE xtr_class_id INT;
  SELECT 0
        ,1
        ,0
        ,0
        ,0
    INTO found
        ,sigma
        ,iclass_id
        ,cat_class_id
        ,xtr_class_id
  ;

  SET ixy = COS(radians(idecl));
  SET ix = ixy * COS(radians(ira));
  SET iy = ixy * SIN(radians(ira));
  SET iz = SIN(radians(idecl));
  SET itheta = ABS(iassoc_angle);
  /* For now, we set it to 1 */
  /*SET iband = getBand(ifreq_eff, 10);*/
  SET iband = 1;

  /**
   * TODO: This is a bug in MonetDB, NULL will be inserted. 
   * Niels is working on it.
   * SELECT zoneheight INTO izoneheight FROM zoneheight;
   * Therefor we set, because we still wok with 1 degree zones:
   */
  SET izoneheight = 1;
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
      SELECT COUNT(*)
        INTO nassoc_catsrcid
        FROM cataloguesources
       WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                      AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
         AND ra BETWEEN ira - ialpha
                    AND ira + ialpha
         AND decl BETWEEN idecl - itheta
                      AND idecl + itheta
         AND (ix * x + iy * y + iz * z) > COS(radians(itheta))
         AND cat_id = icat_id
      ;
      IF nassoc_catsrcid > 0 THEN
        SELECT catsrcid
          INTO iassoc_catsrcid
          FROM cataloguesources
         WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                        AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
           AND ra BETWEEN ira - ialpha
                      AND ira + ialpha
           AND decl BETWEEN idecl - itheta
                        AND idecl + itheta
           AND (ix * x + iy * y + iz * z) > COS(radians(itheta))
           AND cat_id = icat_id
           AND degrees(ACOS(ix * x + iy * y + iz * z)) = (SELECT MIN(degrees(ACOS(ix * x + iy * y + iz * z)))
                                                            FROM cataloguesources
                                                           WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                                                                          AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
                                                             AND ra BETWEEN ira - ialpha
                                                                        AND ira + ialpha
                                                             AND decl BETWEEN idecl - itheta
                                                                          AND idecl + itheta
                                                             AND (ix * x + iy * y + iz * z) > COS(radians(itheta))
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
    ELSE
      IF nassoc_catsrcid > 1 THEN
        SET cat_class_id = 2000 + 100 * (sigma - 1);
      END IF;
    END IF;

  END IF;

  IF (assoc_xtr = TRUE) THEN
    SET found = FALSE;
    SET sigma = 1;
    SET itheta = ABS(iassoc_angle);
    WHILE (found = FALSE AND sigma < 4) DO
      SELECT COUNT(*)
        INTO nassoc_xtrsrcid
        FROM extractedsources
       WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                      AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
         AND ra BETWEEN ira - ialpha
                    AND ira + ialpha
         AND decl BETWEEN idecl - itheta
                      AND idecl + itheta
         AND (ix * x + iy * y + iz * z) > COS(radians(itheta))
         AND ds_id = ids_id
         AND seq_nr = iseq_nr - 1
      ;
      IF nassoc_xtrsrcid > 0 THEN
        SELECT assoc_xtrsrcid
          INTO iassoc_xtrsrcid
          FROM extractedsources
         WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                        AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
           AND ra BETWEEN ira - ialpha
                      AND ira + ialpha
           AND decl BETWEEN idecl - itheta
                        AND idecl + itheta
           AND (ix * x + iy * y + iz * z) > COS(radians(itheta))
           AND ds_id = ids_id
           AND seq_nr = iseq_nr - 1
           AND degrees(ACOS(ix * x + iy * y + iz * z)) = (SELECT MIN(degrees(ACOS(ix * x + iy * y + iz * z)))
                                                            FROM extractedsources
                                                           WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                                                                          AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
                                                             AND ra BETWEEN ira - ialpha
                                                                        AND ira + ialpha
                                                             AND decl BETWEEN idecl - itheta
                                                                          AND idecl + itheta
                                                             AND (ix * x + iy * y + iz * z) > COS(radians(itheta))
                                                             AND ds_id = ids_id
                                                             AND seq_nr = seq_nr - 1
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

    IF nassoc_xtrsrcid = 1 THEN
      SET xtr_class_id = 10 + sigma - 1;
    ELSE
      IF nassoc_xtrsrcid > 1 THEN
        SET xtr_class_id = 20 + sigma - 1;
      END IF;
    END IF;
  END IF;

  SET iclass_id = cat_class_id + xtr_class_id;

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
    ,CAST(FLOOR(idecl/izoneheight) AS INTEGER)
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

  UPDATE extractedsources
     SET assoc_xtrsrcid = xtrsrcid
   WHERE assoc_xtrsrcid IS NULL
  ;

END;

/**
 * This procedure creates a new entry in the datasets table.
 * If the dataset name (dsinname) already exists, the rerun number
 * will be incremented.
 * To keep things analogue with MySQL we have odsid in the arguments,
 * which is the dsid that will be used in this procedure
 */
CREATE PROCEDURE InsertDataset(idsinname VARCHAR(50)
                              ,odsid INT
                              )
BEGIN

  DECLARE idsid INT;
  /* For now this is set to 1 */
  DECLARE irerun INT;
  DECLARE iobs_id INT;
  DECLARE ires_id INT;
  DECLARE idstype TINYINT;
  SELECT NULL
        ,1
        ,1
        ,1
    INTO irerun
        ,iobs_id
        ,ires_id
        ,idstype
  ;
  DECLARE itaustart_timestamp BIGINT;

  SET itaustart_timestamp = REPLACE(REPLACE(REPLACE(NOW(), '-', ''), ' ', ''), ':', '');

  SELECT MAX(rerun)
    INTO irerun
    FROM datasets
   WHERE dsinname = idsinname
  ;

  IF irerun IS NULL THEN
    SET irerun = 0;
  ELSE 
    SET irerun = irerun + 1;
  END IF;

  SELECT NEXT VALUE FOR seq_datasets INTO idsid;

  INSERT INTO datasets
    (dsid
    ,rerun
    ,obs_id
    ,res_id
    ,dstype
    ,taustart_timestamp
    ,dsinname
    ) VALUES
    (idsid
    ,irerun
    ,iobs_id
    ,ires_id
    ,idstype
    ,itaustart_timestamp
    ,idsinname
    )
  ;
  
  SET odsid = idsid;

END;

/**
 * This procedure initialises specific tables in the pipeline database
 * after it is created successfully.
 *
CREATE PROCEDURE InitPipeline()
BEGIN

  TODO: To be implemented in combination with InitObservation() 

END;*/

/**
 * This procedure initialises the pipeline database after it is created
 * successfully.
 */
CREATE PROCEDURE InitObservation(izoneheight DOUBLE
                                ,itheta DOUBLE
                                )
BEGIN

  /* No recursive procedure calls allowed in MonetDB
  /*CALL BuildZones(izoneheight, itheta);*/
  
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
    ,'test images'
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

END;

/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|                           THE END                                 |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */

