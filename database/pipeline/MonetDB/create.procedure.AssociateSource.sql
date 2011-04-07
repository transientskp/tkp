SET SCHEMA pipeline;

DROP PROCEDURE AssociateSource;

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
 * NOTE: USE CAST( AS INTEGER) for zone columns
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
                                ,idet_sigma DOUBLE
                                )
BEGIN

  DECLARE ix DOUBLE;
  DECLARE iy DOUBLE;
  DECLARE iz DOUBLE;
  DECLARE ixy DOUBLE;
  /* For now, we default to the wenss catalogue
  for source asscociation */
  DECLARE icat_id INT;
  SELECT 2 INTO icat_id;

  DECLARE izoneheight DOUBLE;
  DECLARE itheta DOUBLE;
  DECLARE ialpha DOUBLE;
  DECLARE iback INT;

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

  SET ixy = COS(RADIANS(idecl));
  SET ix = ixy * COS(RADIANS(ira));
  SET iy = ixy * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));
  /*SET itheta = ABS(iassoc_angle);*/
  /*SET iband = getBand(ifreq_eff, 10);*/
  SELECT 1 INTO iband;

  SELECT zoneheight INTO izoneheight FROM zoneheight;
  /* For this we set itheta to 10 arcsec
  SELECT GREATEST(ira_err, idecl_err) INTO itheta;*/
  SET itheta = 10/3600; /* in degrees */
  SET ialpha = alpha(itheta, idecl);

  /**
   * With these source association can be run on
   * catalogue or extractedsources only. The variables
   * are internal.
   */
  SET assoc_xtr = TRUE;
  SET assoc_cat = TRUE;

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
       WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                      AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
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
         WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                        AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
           AND ra BETWEEN ira - ialpha
                      AND ira + ialpha
           AND decl BETWEEN idecl - itheta
                        AND idecl + itheta
           AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
           AND cat_id = icat_id
           AND DEGREES(ACOS(ix * x + iy * y + iz * z)) = 
                (SELECT MIN(DEGREES(ACOS(ix * x + iy * y + iz * z)))
                   FROM cataloguesources
                  WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                                 AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
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
     * Therefore we will do some tests on this source, 
     * to see if it existed in the PREVIOUS images (or not).
     * If the source cannot be associated the search radius will be 
     * incremented by a maximum of three times the radius. If it is then 
     * still not found, we will look back one more image. As soon
     * as the source can be associated it will stop.
     * Sources that cannot be associated will get the same
     * assoc_xtrsrcid as xtrsrcid.
     * In this way even sources in non-overlapping fields will get an 
     * assoc_xtrsrcid value (if it was not detected before).
     */
    SET found = FALSE;
    SET sigma = 1;
    /*SELECT GREATEST(ira_err, idecl_err) INTO itheta;*/
    SET itheta = 10/3600;
    WHILE (found = FALSE AND sigma < 4) DO
      SET iback = 1;
      WHILE (found = FALSE AND (iseq_nr >= iback)) DO
        /* Analogous to catalogue case*/
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
           AND ds_id = ids_id
           AND seq_nr = iseq_nr - iback
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
             AND ds_id = ids_id
             AND seq_nr = iseq_nr - iback
             AND DEGREES(ACOS(ix * x + iy * y + iz * z)) = 
                (SELECT MIN(DEGREES(ACOS(ix * x + iy * y + iz * z)))
                   FROM extractedsources
                  WHERE zone BETWEEN CAST(FLOOR((idecl - itheta)/izoneheight) AS INTEGER)
                                 AND CAST(FLOOR((idecl + itheta)/izoneheight) AS INTEGER)
                    AND ra BETWEEN ira - ialpha
                               AND ira + ialpha
                    AND decl BETWEEN idecl - itheta
                                 AND idecl + itheta
                    AND (ix * x + iy * y + iz * z) > COS(RADIANS(itheta))
                    AND ds_id = ids_id
                    AND seq_nr = iseq_nr - iback
                )
          ;
        END IF;
        IF nassoc_xtrsrcid > 0 THEN
          SET found = TRUE;
        ELSE 
          SET iback = iback + 1;
        END IF;
      END WHILE;
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
    /*,det_sigma*/
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
    /*,idet_sigma*/
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

