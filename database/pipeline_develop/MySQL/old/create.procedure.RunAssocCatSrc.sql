DROP PROCEDURE IF EXISTS RunAssocCatSrc;

DELIMITER //

/*+------------------------------------------------------------------+
 *| This procedure                                                   |
 *+------------------------------------------------------------------+
 *| Input params:                                                    |
 *+------------------------------------------------------------------+
 *| Used variables:                                                  |
 *| itheta: this is the radius (in degrees) of the circular area     |
 *|         centered at (ra,decl) of the current (input) source. All |
 *|         sources found within this area will be inspected for     |
 *|         association.                                             |
 *|         The difficult part is how to determine what is the best  |
 *|         value for itheta. Will it depend on the source density,  |
 *|         which depends on int.time, freq, or is it sufficient to  |
 *|         simply set it to a default value of f.ex. 1 (degree)?    |
 *|         For now, we default it to 1 (degree).                    |
 *|                                                                  |
 *+------------------------------------------------------------------+
 *| TODO: Also insert margin records                                 |
 *+------------------------------------------------------------------+
 *|                       Bart Scheers                               |
 *|                        2009-02-18                                |
 *+------------------------------------------------------------------+
 *| 2009-02-18                                                       |
 *| Based on AssociateSource() from create.database.sql              |
 *+------------------------------------------------------------------+
 *| Open Questions:                                                  |
 *|                                                                  |
 *+------------------------------------------------------------------+
 */
CREATE PROCEDURE RunAssocCatSrc()
BEGIN

  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR
    SELECT catsrccid
          ,cat_id
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,x
          ,y
          ,z
          ,i_peak_avg
          ,i_peak_avg_err
          ,i_int_avg
          ,i_int_avg_err
      FROM cataloguedsources
     WHERE cat_id = icat_id
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
          ,ix
          ,iy
          ,iz
          ,ii_peak_avg
          ,ii_peak_avg_err
          ,ii_int_avg
          ,ii_int_avg_err
      ;
      IF NOT done THEN
        CALL AssocCatSrc(icatsrcid
                        ,icat_id
                        ,ira
                        ,idecl
                        ,ira_err
                        ,idecl_err
                        ,ix
                        ,iy
                        ,iz
                        ,ii_peak_avg
                        ,ii_peak_avg_err
                        ,ii_int_avg
                        ,ii_int_avg_err
                        );

      END IF;
    UNTIL done END REPEAT;
  CLOSE cur1;

END;
//

DELIMITER ;

