--DROP PROCEDURE LoadLSM; 
/*+-------------------------------------------------------------------+
 *| This script loads the pipeline.extractedsources table with the    |
 *| WENSS sources (which are selected from the catalogedsources table)|
 *+-------------------------------------------------------------------+
 *+-------------------------------------------------------------------+
 *+-------------------------------------------------------------------+
 */

CREATE PROCEDURE LoadLSM(ira_min DOUBLE
                        ,ira_max DOUBLE
                        ,idecl_min DOUBLE
                        ,idecl_max DOUBLE
                        ,icatname1 VARCHAR(50)
                        ,icatname2 VARCHAR(50)
                        ,icatname3 VARCHAR(50)
                        )
BEGIN

  DECLARE izoneheight DOUBLE;

  /*TODO
  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight 
  ;*/
  SET izoneheight = 1.0;

  INSERT INTO lsm
    SELECT cs.* 
      FROM catalogedsources cs
          ,catalogs c
     WHERE cat_id = catid
       AND (catname = UPPER(icatname1)
            OR catname = UPPER(icatname2)
            OR catname = UPPER(icatname3)
           )
       AND zone BETWEEN CAST(FLOOR(idecl_min / izoneheight) AS INTEGER)
                    AND CAST(FLOOR(idecl_max / izoneheight) AS INTEGER)
       AND decl BETWEEN idecl_min 
                    AND idecl_max
       AND ra BETWEEN ira_min
                  AND ira_max
       AND (src_type IS NULL 
            /*OR src_type IN ('S')*/
            OR src_type IN ('S', 'C')
           )
       AND fit_probl IS NULL
  ;

END;

