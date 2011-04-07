SET SCHEMA pipeline;

/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|                    This section describes                         |
 *|                 the functions and procedures                      |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *| It is split from the database and table creation part, because    |
 *| the analogue of MySQL's LAST_INSERT_ID() is not straightforward.  |
 *| We have to SELECT NEXT VALUE FOR seq_nnnn. And this has to be     |
 *| looked up after the table is created.                             |
 *+-------------------------------------------------------------------+
 *| TODO: Make the next value easier.                                 |
 *+-------------------------------------------------------------------+
 *| Bart Scheers 2008-08-08                                           |
 *+-------------------------------------------------------------------+
 */

DROP PROCEDURE InitObservation;
DROP PROCEDURE InitPipeline;
DROP PROCEDURE InsertDataset;
DROP PROCEDURE AssociateSource;
DROP PROCEDURE BuildZones;

DROP FUNCTION getBand;
DROP FUNCTION alpha;
DROP FUNCTION radians;
DROP FUNCTION degrees;

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
    
  IF ISNULL(ofreqbandid) THEN
    /* TODO: This has to looked up */
    SELECT NEXT VALUE FOR seq_7085 INTO ifreqbandid;
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
  END IF;
  
  SET ofreqbandid = ifreqbandid;

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

  DELETE FROM zoneheight;
  DELETE FROM zones;
  DELETE FROM zonezone;

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
   */
  SELECT zoneheight INTO izoneheight FROM zoneheight;
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
 */
CREATE PROCEDURE InsertDataset(idsinname VARCHAR(50)
                              ,odsid INT
                              )
BEGIN

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

  IF ISNULL(irerun) THEN
    SET irerun = 0;
  ELSE 
    SET irerun = irerun + 1;
  END IF;

  /* TODO: We have to look this number up after creation */
  SELECT NEXT VALUE FOR seq_7094 INTO idsid;

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

