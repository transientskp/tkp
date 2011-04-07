SET SCHEMA "pipeline";

CREATE PROCEDURE AssociateSource(itau INT
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
  DECLARE iclass_id INT;

  DECLARE assoc_xtr BOOLEAN;
  SET assoc_xtr = TRUE;
  DECLARE assoc_cat BOOLEAN;
  SET assoc_xtr = TRUE;

  SET ixy = COS(RADIANS(idecl));
  SET ix = ixy * COS(RADIANS(ira));
  SET iy = ixy * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  SELECT zoneheight INTO izoneheight FROM zoneheight;
  SELECT CASE WHEN ira_err > idecl_err THEN ira_err ELSE idecl_err END INTO itheta;
  SET ialpha = alpha(itheta, idecl);

  SET assoc_xtr = TRUE;
  SET assoc_cat = TRUE;

  IF (assoc_cat = TRUE) THEN
    SELECT CASE WHEN COUNT(catsrcid) > 0
                THEN catsrcid
                ELSE NULL
                END
          ,COUNT(catsrcid)
      INTO iassoc_catsrcid
          ,nassoc_catsrcid
      FROM cataloguesources
     WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight) 
                    AND FLOOR((idecl + itheta)/izoneheight)
       AND ra BETWEEN ira - ialpha 
                  AND ira + ialpha
       AND decl BETWEEN idecl - itheta 
                    AND idecl + itheta
       AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
    ;
  END IF;  

  IF (assoc_xtr = TRUE) THEN
    SELECT CASE WHEN COUNT(assoc_xtrsrcid) > 0
                THEN assoc_xtrsrcid
                ELSE NULL
                END
          ,COUNT(assoc_xtrsrcid)
      INTO iassoc_xtrsrcid
          ,nassoc_xtrsrcid
      FROM extractedsources
     WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight) 
                    AND FLOOR((idecl + itheta)/izoneheight)
       AND ra BETWEEN ira - ialpha 
                  AND ira + ialpha
       AND decl BETWEEN idecl - itheta 
                    AND idecl + itheta
       AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
       AND seq_nr = iseq_nr - 1
    ;
  END IF;

  IF (nassoc_catsrcid = 0) THEN
    IF (nassoc_xtrsrcid > 1) THEN
      SET iclass_id = 6;
    END IF;
  ELSEIF (nassoc_catsrcid = 1) THEN
    IF (nassoc_xtrsrcid > 1) THEN
      SET iclass_id = 6;
    END IF;
  ELSEIF (nassoc_catsrcid > 1) THEN
    IF (nassoc_xtrsrcid = 0) THEN
      SET iclass_id = 7;
    ELSEIF (nassoc_xtrsrcid = 1) THEN
      SET iclass_id = 7;
    ELSEIF (nassoc_xtrsrcid > 1) THEN
      SET iclass_id = 7;
    END IF;
  END IF;

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
    )
  ;

  UPDATE extractedsources
     SET assoc_xtrsrcid = xtrsrcid
   WHERE assoc_xtrsrcid IS NULL
  ;

END;

/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|                           THE END                                 |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */

