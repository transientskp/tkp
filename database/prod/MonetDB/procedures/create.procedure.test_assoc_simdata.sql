DROP PROCEDURE IF EXISTS test_assoc_simdata;

DELIMITER //

CREATE PROCEDURE test_assoc_simdata()
BEGIN

  DECLARE ixtrsrcid INT;
  DECLARE ifile_id INT;
  DECLARE itaustart_timestamp BIGINT;
  DECLARE itau INT;
  DECLARE iband INT;
  DECLARE iseq_nr INT;
  DECLARE ira DOUBLE;
  DECLARE idecl DOUBLE;
  DECLARE ira_err DOUBLE;
  DECLARE idecl_err DOUBLE;
  DECLARE idet_sigma DOUBLE;
  DECLARE ii_peak DOUBLE;
  DECLARE ii_int DOUBLE;
  DECLARE ii_peak_err DOUBLE;
  DECLARE ii_int_err DOUBLE;

  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR
    SELECT xtrsrcid
          ,file_id
          ,taustart_timestamp
          ,tau
          ,band
          ,seq_nr
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,det_sigma
          ,i_peak
          ,i_peak_err
          ,i_int
          ,i_int_err
      FROM extractedsources
          ,files
     WHERE file_id = fileid
     ;     
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  OPEN cur1;
    REPEAT
      FETCH cur1
       INTO ixtrsrcid
           ,ifile_id
           ,itaustart_timestamp
           ,itau
           ,iband
           ,iseq_nr
           ,ira
           ,idecl
           ,ira_err
           ,idecl_err
           ,idet_sigma
           ,ii_peak
           ,ii_peak_err
           ,ii_int
           ,ii_int_err
      ;
      IF NOT done THEN
        CALL AssocXtrXtrSrc(ixtrsrcid
                           ,ifile_id
                           ,itaustart_timestamp
                           ,itau
                           ,iband
                           ,iseq_nr
                           ,ira
                           ,idecl
                           ,ira_err
                           ,idecl_err
                           ,idet_sigma
                           ,iI_peak
                           ,iI_peak_err
                           ,iI_int
                           ,iI_int_err
                           );
      END IF;
    UNTIL done END REPEAT;
  CLOSE cur1;

END;
//

DELIMITER ;

