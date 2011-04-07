USE pipeline;

DROP PROCEDURE IF EXISTS Assoc2XMMiSlim2Wenss;

DELIMITER //

CREATE PROCEDURE Assoc2XMMiSlim2Wenss()

BEGIN

  DECLARE iseq_nr INT DEFAULT 0;
  DECLARE ifreq_eff DOUBLE;
  DECLARE ira DOUBLE;
  DECLARE idecl DOUBLE;
  DECLARE ira_err DOUBLE;
  DECLARE idecl_err DOUBLE;
  DECLARE idet_sigma DOUBLE;
  DECLARE iI_peak_avg DOUBLE;
  DECLARE iI_peak_avg_err DOUBLE;
  DECLARE iI_int_avg DOUBLE;
  DECLARE iI_int_avg_err DOUBLE;
  /* this is the ra and dec increment (deg) in wenss map WN55074 
  DECLARE iassoc_angle DOUBLE DEFAULT 0.00585937;*/
  DECLARE iassoc_angle DOUBLE;
  DECLARE idsid INT DEFAULT NULL;
  DECLARE odsid INT DEFAULT NULL;

  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR
    SELECT freq_eff
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          /*,I_peak_avg
          ,I_peak_avg_err*/
          ,I_int_avg
          ,I_int_avg_err
     FROM cataloguesources
    WHERE cat_id = 4 -- 2XMMi Slim
      AND zone >= 28
    ORDER BY orig_catsrcid;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  CALL InsertDataset('2XMMi Slim assoc Wenss', odsid);
  SET idsid = odsid;

  OPEN cur1;

  REPEAT
    FETCH cur1
     INTO ifreq_eff
         ,ira
         ,idecl
         ,ira_err
         ,idecl_err
         /*,iI_peak_avg
         ,iI_peak_avg_err*/
         ,iI_int_avg
         ,iI_int_avg_err
    ;
    IF NOT done THEN
      SET iassoc_angle = GREATEST(ira_err, idecl_err);
      CALL AssociateSource(1
                          ,iseq_nr
                          ,idsid
                          ,ifreq_eff
                          ,ira
                          ,idecl
                          ,ira_err
                          ,idecl_err
                          ,NULL
                          ,NULL
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

