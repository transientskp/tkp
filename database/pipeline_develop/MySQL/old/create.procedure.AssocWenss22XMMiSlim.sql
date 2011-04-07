DROP PROCEDURE IF EXISTS AssocWenss22XMMiSlim;

DELIMITER //

CREATE PROCEDURE AssocWenss22XMMiSlim()

BEGIN

  DECLARE ira DOUBLE;
  DECLARE idecl DOUBLE;
  DECLARE ira_err DOUBLE;
  DECLARE idecl_err DOUBLE;
  DECLARE iI_peak_avg DOUBLE;
  DECLARE iI_peak_avg_err DOUBLE;
  DECLARE iI_int_avg DOUBLE;
  DECLARE iI_int_avg_err DOUBLE;
  DECLARE idsid INT;
  DECLARE iimage_id INT;

  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR
    SELECT ra
          ,decl
          ,ra_err
          ,decl_err
          ,I_peak_avg
          ,I_peak_avg_err
          ,I_int_avg
          ,I_int_avg_err
     FROM catalogedsources
    WHERE cat_id = 3 -- WENSS
    ORDER BY orig_catsrcid;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  SELECT insertDataset('WENSS assoc 2XMMi Slim') INTO idsid;
  SELECT insertImage(idsid, '/home/bscheers/databases/catalogues/2XMMi/2XMMi-slim.csv') INTO iimage_id;

  OPEN cur1;

  REPEAT
    FETCH cur1
     INTO ira
         ,idecl
         ,ira_err
         ,idecl_err
         ,iI_peak_avg
         ,iI_peak_avg_err
         ,iI_int_avg
         ,iI_int_avg_err
    ;
    IF NOT done THEN
      CALL AssocSrc(iimage_id
                   ,ira
                   ,idecl
                   ,ira_err
                   ,idecl_err
                   ,iI_peak_avg
                   ,iI_peak_avg_err
                   ,iI_int_avg
                   ,iI_int_avg_err
                   ,0
                   );
    END IF;
  UNTIL done END REPEAT;

  CLOSE cur1;

END;
//

DELIMITER ;

