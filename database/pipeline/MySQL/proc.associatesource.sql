use pipeline;

DROP PROCEDURE IF EXISTS AssociateSource;

delimiter //

CREATE PROCEDURE associatesource(IN itau INT
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
                                ,IN ilocal_rms DOUBLE
                                )
BEGIN

  DECLARE ix DOUBLE;
  DECLARE iy DOUBLE;
  DECLARE iz DOUBLE;
  DECLARE ixy DOUBLE;
  
  DECLARE icat_id INT DEFAULT 8;
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
  
  SET ialpha = alpha(itheta, idecl);
  
  SET assoc_xtr = TRUE;
  SET assoc_cat = TRUE;
  IF (assoc_cat = TRUE) THEN
  
    WHILE (found = FALSE AND sigma < 4) DO
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
  
  END IF; 

  IF (assoc_xtr = TRUE) THEN
    SET found = FALSE;
    
    SET sigma = 1;
    
    
    SET itheta = ABS(iassoc_angle);
    
    WHILE (found = FALSE AND sigma < 4) DO
    
    
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
        
        END IF;
        
        IF nassoc_xtrsrcid = 1 THEN
        
        SET xtr_class_id = 10 + sigma - 1;
        
        ELSEIF nassoc_xtrsrcid > 1 THEN
        
        SET xtr_class_id = 20 + sigma - 1;
        
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
        
        ,local_rms
        
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
        
        ,ilocal_rms
        
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
        

        
        //
        
        DELIMITER ;                                                                                              
