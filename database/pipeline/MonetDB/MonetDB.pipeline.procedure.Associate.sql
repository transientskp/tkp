SET SCHEMA pipeline;

DROP PROCEDURE Associate;

CREATE PROCEDURE Associate(itau INT
                                ,iband INT
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
  DECLARE xtr_class_id INT;
  DECLARE cat_class_id INT;
  SELECT 0
        ,1
        ,0
        ,0
        ,0
    INTO found
        ,sigma
        ,iclass_id
        ,xtr_class_id
        ,cat_class_id
  ;

  SET ixy = COS(RADIANS(idecl));
  SET ix = ixy * COS(RADIANS(ira));
  SET iy = ixy * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  SELECT zoneheight INTO izoneheight FROM zoneheight;
  SET ialpha = alpha(itheta, idecl);

  SET assoc_xtr = FALSE;
  SET assoc_cat = FALSE;

  IF (assoc_cat = TRUE) THEN
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
         AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
         AND cat_id = 1
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
           AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
           AND cat_id = 1
           AND DEGREES(ACOS(ix * x + iy * y + iz * z)) = (SELECT MIN(DEGREES(ACOS(ix * x + iy * y + iz * z)))
                                                            FROM cataloguesources
                                                           WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                                                                          AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
                                                             AND ra BETWEEN ira - ialpha
                                                                        AND ira + ialpha
                                                             AND decl BETWEEN idecl - itheta
                                                                          AND idecl + itheta
                                                             AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
                                                             AND cat_id = 1
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
         AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
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
           AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
           AND seq_nr = iseq_nr - 1
           AND DEGREES(ACOS(ix * x + iy * y + iz * z)) = (SELECT MIN(DEGREES(ACOS(ix * x + iy * y + iz * z)))
                                                            FROM extractedsources
                                                           WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                                                                          AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
                                                             AND ra BETWEEN ira - ialpha
                                                                        AND ira + ialpha
                                                             AND decl BETWEEN idecl - itheta
                                                                          AND idecl + itheta
                                                             AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
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

