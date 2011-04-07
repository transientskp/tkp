USE pipeline;

DROP PROCEDURE IF EXISTS SAD2FPOS0370;

DELIMITER //

CREATE PROCEDURE SAD2FPOS0370()

BEGIN

  DECLARE iorig_catsrcid INT;
  DECLARE ifreq_eff DOUBLE;
  DECLARE ira DOUBLE;
  DECLARE idecl DOUBLE;
  DECLARE ira_err DOUBLE;
  DECLARE idecl_err DOUBLE;
  DECLARE iI_peak DOUBLE;
  DECLARE iI_peak_err DOUBLE;
  DECLARE iI_int DOUBLE;
  DECLARE iI_int_err DOUBLE;
  /* this is the ra and dec increment (deg) in wenss map WN55074 */
  DECLARE iassoc_angle DOUBLE /*DEFAULT 0.00585937*/;
  DECLARE icat_id INT;

  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR
    SELECT orig_catsrcid
          ,freq_eff
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,I_peak_avg
          ,I_peak_avg_err
          ,I_int_avg
          ,I_int_avg_err
     FROM cataloguesources
    WHERE cat_id = 4;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  OPEN cur1;

  REPEAT
    FETCH cur1
     INTO iorig_catsrcid
         ,ifreq_eff
         ,ira
         ,idecl
         ,ira_err
         ,idecl_err
         ,iI_peak
         ,iI_peak_err
         ,iI_int
         ,iI_int_err
    ;
    IF NOT done THEN
      CALL AssociateSource(1
                          ,iorig_catsrcid
                          ,26
                          ,ifreq_eff
                          ,ira
                          ,idecl
                          ,ira_err
                          ,idecl_err
                          ,iI_peak
                          ,iI_peak_err
                          ,iI_int
                          ,iI_int_err
                          ,ira_err
                          ,iorig_catsrcid + 100
                          );
    END IF;
  UNTIL done END REPEAT;

  CLOSE cur1;

END;
//

DELIMITER ;

/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|                           THE END                                 |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */

