USE pipeline;

DROP PROCEDURE IF EXISTS AssocWenss2Vlss;

DELIMITER //

CREATE PROCEDURE AssocWenss2Vlss()

BEGIN

  DECLARE iseq_nr INT;
  DECLARE ifreq_eff DOUBLE;
  DECLARE ira DOUBLE;
  DECLARE idecl DOUBLE;
  DECLARE ira_err DOUBLE;
  DECLARE idecl_err DOUBLE;
  DECLARE idet_sigma DOUBLE;
  DECLARE iI_peak DOUBLE;
  DECLARE iI_peak_err DOUBLE;
  DECLARE iI_int DOUBLE;
  DECLARE iI_int_err DOUBLE;
  /* this is the ra and dec increment (deg) in wenss map WN55074 */
  DECLARE iassoc_angle DOUBLE DEFAULT 0.00585937;

  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR
    SELECT seq_nr
          ,freq_eff
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,local_rms
          ,I_peak
          ,I_peak_err
          ,I_int
          ,I_int_err
     FROM extractedsources
    WHERE ds_id = 532
    ORDER BY seq_nr
            ,xtrsrcid;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  OPEN cur1;

  REPEAT
    FETCH cur1
     INTO iseq_nr
         ,ifreq_eff
         ,ira
         ,idecl
         ,ira_err
         ,idecl_err
         ,idet_sigma
         ,iI_peak
         ,iI_peak_err
         ,iI_int
         ,iI_int_err
    ;
    IF NOT done THEN
      CALL AssociateSource(1
                          ,iseq_nr
                          ,533
                          ,ifreq_eff
                          ,ira
                          ,idecl
                          ,ira_err
                          ,idecl_err
                          ,iI_peak
                          ,iI_peak_err
                          ,iI_int
                          ,iI_int_err
                          ,iassoc_angle
                          ,idet_sigma
                          );
    END IF;
  UNTIL done END REPEAT;

  CLOSE cur1;

END;
//

DELIMITER ;

