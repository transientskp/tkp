DROP PROCEDURE IF EXISTS AssocXtrXtrSrc;

DELIMITER //

CREATE PROCEDURE AssocXtrXtrSrc(IN ixtrsrcid INT
                               ,IN ifile_id INT
                               ,IN taustart_timestamp BIGINT
                               ,IN itau INT
                               ,IN iband INT
                               ,IN iseq_nr INT
                               ,IN ira DOUBLE
                               ,IN idecl DOUBLE
                               ,IN ira_err DOUBLE
                               ,IN idecl_err DOUBLE
                               ,IN iI_peak DOUBLE
                               ,IN iI_peak_err DOUBLE
                               ,IN iI_int DOUBLE
                               ,IN iI_int_err DOUBLE
                               ,IN idet_sigma DOUBLE
                               )
BEGIN

  DECLARE ix DOUBLE;
  DECLARE iy DOUBLE;
  DECLARE iz DOUBLE;
  DECLARE ixy DOUBLE;

  DECLARE izoneheight DOUBLE DEFAULT 1;
  DECLARE itheta DOUBLE;
  DECLARE ialpha DOUBLE;
  DECLARE seq_back INT;
  DECLARE band_back INT;

  DECLARE iassoc_xtrsrcid INT DEFAULT NULL;
  DECLARE nassoc_xtrsrcid INT DEFAULT 0;
  DECLARE iassoc_catsrcid INT DEFAULT NULL;
  DECLARE nassoc_catsrcid INT DEFAULT 0;
  DECLARE ifirst_xtrsrcid INT;

  DECLARE found BOOLEAN DEFAULT FALSE;
  DECLARE sigma INT DEFAULT 1;
  DECLARE iclass_id INT DEFAULT 0;
  DECLARE cat_class_id INT DEFAULT 0;
  DECLARE xtr_class_id INT DEFAULT 0;

  SET ixy = COS(RADIANS(idecl));
  SET ix = ixy * COS(RADIANS(ira));
  SET iy = ixy * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  SELECT GREATEST(ira_err, idecl_err) INTO itheta;
  SET ialpha = alpha(itheta, idecl);

  SET found = FALSE;
  SET sigma = 1;
  SELECT GREATEST(ira_err, idecl_err) INTO itheta;
  WHILE (found = FALSE AND sigma < 4) DO
    SET seq_back = 1;
    WHILE (found = FALSE AND (iseq_nr >= seq_back)) DO
      SELECT COUNT(*)
        INTO nassoc_xtrsrcid
        FROM extractedsources
            ,files
       WHERE file_id = fileid
         AND tau = itau
         AND band = iband
         AND seq_nr = iseq_nr - seq_back
         AND zone BETWEEN FLOOR((idecl - itheta)/izoneheight) 
                      AND FLOOR((idecl + itheta)/izoneheight)
         AND ra BETWEEN ira - ialpha 
                AND ira + ialpha
         AND decl BETWEEN idecl - itheta 
                      AND idecl + itheta
         AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
         AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                            ,ra,decl,ra_err,decl_err)
      ;
      IF nassoc_xtrsrcid > 0 THEN
        SELECT xtrsrcid
          INTO iassoc_xtrsrcid
          FROM extractedsources
              ,files
         WHERE file_id = fileid
           AND tau = itau
           AND band = iband
           AND seq_nr = iseq_nr - seq_back
           AND zone BETWEEN FLOOR((idecl - itheta)/izoneheight) 
                        AND FLOOR((idecl + itheta)/izoneheight)
           AND ra BETWEEN ira - ialpha 
                      AND ira + ialpha
           AND decl BETWEEN idecl - itheta 
                        AND idecl + itheta
           AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
           AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                              ,ra,decl,ra_err,decl_err)
        ;
        SET found = TRUE;
        SELECT xtrsrc_id
          INTO ifirst_xtrsrcid
          FROM associatedsources
         WHERE assoc_xtrsrcid = iassoc_xtrsrcid
        ;
      ELSE
        SET seq_back = seq_back + 1;
      END IF;
    END WHILE;
    IF nassoc_xtrsrcid = 0 THEN
      SET sigma = sigma + 1;
      SET itheta = sigma * itheta / (sigma - 1);
      SET ialpha = alpha(itheta, idecl);
    END IF;
  END WHILE;

  IF nassoc_xtrsrcid = 0 THEN
    SET ifirst_xtrsrcid = ixtrsrcid;
    SET ixtrsrcid = ifirst_xtrsrcid;
  END IF;

  INSERT INTO associatedsources
    (xtrsrc_id
    ,assoc_xtrsrcid
    )
  VALUES
    (ifirst_xtrsrcid
    ,ixtrsrcid
    )
  ;

END;
//

DELIMITER ;

