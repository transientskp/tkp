DROP PROCEDURE IF EXISTS CollectAssocSrcs;

DELIMITER //


/**
 * These series of procedures should only be executed at the end of
 * an observation or a defined point in time when processing the 
 * images belonging to a dataset has come to an end.
 * 
 * We cursor through the associatedsources table
 * order by xtrsrc_id, assoc_xtrsrcid
 *
 * NOTE: cursoring is not the fastest way to do
 * this, so this must be converted in a single
 * query.
 *
 */
CREATE PROCEDURE CollectAssocSrcs(IN ids_id INT)
BEGIN

  DECLARE ixtrsrc_id INT;
  DECLARE isrc_type CHAR(1);
  DECLARE iassoc_xtrsrcid INT;
  DECLARE iassoc_catsrcid INT;
  DECLARE iassoc_class_id INT;
  
  DECLARE done INT DEFAULT 0;
  /* Here we select all the sources that were 
   * detected in the specified dataset
   */
  DECLARE cur1 CURSOR FOR
    SELECT xtrsrc_id
          ,src_type
          ,assoc_xtrsrcid
          ,assoc_catsrcid
          ,assoc_class_id
      FROM associatedsources
          ,extractedsources 
          ,images
     WHERE xtrsrc_id = xtrsrcid
       AND image_id = imageid
       AND ds_id = ids_id
       AND assoc_xtrsrcid IS NOT NULL
       /* how do we set src_type ? */
    ORDER BY xtrsrc_id
            ,assoc_xtrsrcid
  ;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  DELETE FROM aux_associatedsources;

  OPEN cur1;
    REPEAT
      FETCH cur1
       INTO ixtrsrc_id
           ,isrc_type
           ,iassoc_xtrsrcid
           ,iassoc_catsrcid
           ,iassoc_class_id
      ;
      IF NOT done THEN
        CALL CollectForDump(ixtrsrc_id, iassoc_xtrsrcid);
      END IF;
    UNTIL done END REPEAT;
  CLOSE cur1;

  /* And here we can dump the contents of aux_associatedsources 
   * after which we can delete the table, and 
   * are done
   */

  CALL DumpPipeline();

END;
//

DELIMITER ;

