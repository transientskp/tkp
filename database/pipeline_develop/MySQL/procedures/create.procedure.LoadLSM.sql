DROP PROCEDURE IF EXISTS LoadLSM; 

DELIMITER //

/*+-------------------------------------------------------------------+
 *| This script loads the pipeline.extractedsources table with the    |
 *| WENSS sources (which are selected from the catalogedsources table)|
 *+-------------------------------------------------------------------+
 *+-------------------------------------------------------------------+
 *+-------------------------------------------------------------------+
 */

CREATE PROCEDURE LoadLSM(IN ira_min DOUBLE
                        ,IN ira_max DOUBLE
                        ,IN idecl_min DOUBLE
                        ,IN idecl_max DOUBLE
                        ,IN icatname1 VARCHAR(50)
                        ,IN icatname2 VARCHAR(50)
                        ,IN icatname3 VARCHAR(50)
                        )
BEGIN

  DECLARE izoneheight DOUBLE;

  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight 
  ;

  INSERT INTO lsm
    SELECT cs.* 
      FROM catalogedsources cs
          ,catalogs c
     WHERE cat_id = catid
       AND (catname = UPPER(icatname1)
            OR catname = UPPER(icatname2)
            OR catname = UPPER(icatname3)
           )
       AND zone BETWEEN FLOOR(idecl_min / izoneheight)
                    AND FLOOR(idecl_max / izoneheight)
       AND decl BETWEEN idecl_min 
                    AND idecl_max
       AND ra BETWEEN ira_min
                  AND ira_max
  ;

END;
//

DELIMITER ;

