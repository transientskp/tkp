USE pipeline_test;

DROP PROCEDURE IF EXISTS test_assoc_catdata;

DELIMITER //

CREATE PROCEDURE test_assoc_catdata()
BEGIN

  DECLARE icatsrcid INT;
  DECLARE icat_id INT;
  DECLARE ira double precision;
  DECLARE idecl double precision;
  DECLARE ira_err double precision;
  DECLARE idecl_err double precision;

  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR
    SELECT catsrcid
          ,cat_id
          ,ra
          ,decl
          ,ra_err
          ,decl_err
      FROM cataloguedsources
     ;     
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  OPEN cur1;
    REPEAT
      FETCH cur1
       INTO icatsrcid
           ,icat_id
           ,ira
           ,idecl
           ,ira_err
           ,idecl_err
      ;
      IF NOT done THEN
        CALL AssocCatCatSrc(icatsrcid
                           ,icat_id
                           ,ira
                           ,idecl
                           ,ira_err
                           ,idecl_err
                           );
      END IF;
    UNTIL done END REPEAT;
  CLOSE cur1;

END;
//

DELIMITER ;

