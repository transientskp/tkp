USE pipeline;

DROP PROCEDURE IF EXISTS AssocVlss2Wenss;

DELIMITER //

/*
 * Input arg is dsid
 */
CREATE PROCEDURE AssocVlss2Wenss(IN idsid INT)

BEGIN

  DECLARE ifreq_eff DOUBLE;
  DECLARE ira DOUBLE;
  DECLARE idecl DOUBLE;
  DECLARE ira_err DOUBLE;
  DECLARE idecl_err DOUBLE;
  DECLARE iI_peak_avg DOUBLE;
  DECLARE iI_peak_avg_err DOUBLE;
  DECLARE iI_int_avg DOUBLE;
  DECLARE iI_int_avg_err DOUBLE;
  /* this is the ra and dec increment (deg) in wenss map WN55074 */
  DECLARE iassoc_angle DOUBLE DEFAULT 0.00585937;

  DECLARE done INT DEFAULT 0;
  
  DECLARE cur1 CURSOR FOR
    SELECT freq_eff
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,I_peak_avg
          ,I_peak_avg_err
          ,I_int_avg
          ,I_int_avg_err
     FROM cataloguesources
    WHERE cat_id = 8
      AND zone >= 30
      /*AND orig_catsrcid = 14681 
      /*AND orig_catsrcid <> 23980 */
    ORDER BY orig_catsrcid
    ;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  OPEN cur1;

  REPEAT
    FETCH cur1
     INTO ifreq_eff
         ,ira
         ,idecl
         ,ira_err
         ,idecl_err
         ,iI_peak_avg
         ,iI_peak_avg_err
         ,iI_int_avg
         ,iI_int_avg_err
    ;
    IF NOT done THEN
      CALL AssociateSource(1
                          ,0
                          ,idsid
                          ,ifreq_eff
                          ,ira
                          ,idecl
                          ,ira_err
                          ,idecl_err
                          ,iI_peak_avg
                          ,iI_peak_avg_err
                          ,iI_int_avg
                          ,iI_int_avg_err
                          ,iassoc_angle
                          ,0
                          );
    END IF;
  UNTIL done END REPEAT;

  CLOSE cur1;

END;
//

DELIMITER ;

