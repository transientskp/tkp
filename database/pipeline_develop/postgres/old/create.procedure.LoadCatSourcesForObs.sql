--DROP PROCEDURE LoadCatSourcesForObs; 
/*+-------------------------------------------------------------------+
 *| This script loads the pipeline.extractedsources table with the    |
 *| WENSS sources (which are selected from the catalogedsources table)|
 *+-------------------------------------------------------------------+
 *+-------------------------------------------------------------------+
 *+-------------------------------------------------------------------+
 */

CREATE PROCEDURE LoadCatSourcesForObs(idecl_min DOUBLE
                                     ,idecl_max DOUBLE
                                     ,icatname1 VARCHAR(50)
                                     ,icatname2 VARCHAR(50)
                                     ,icatname2 VARCHAR(50)
                                     )
BEGIN

  DECLARE izoneheight DOUBLE;

  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight 
  ;

  INSERT INTO obscatsources
    SELECT cs.* 
      FROM catalogedsources cs
          ,catalogs c
     WHERE cat_id = catid
       AND (catname = icatname1
            OR catname = UPPER(icatname2)
            OR catname = UPPER(icatname2)
           )
       AND zone BETWEEN CAST(FLOOR(idecl_min / izoneheight) AS INTEGER)
                    AND CAST(FLOOR(idecl_max / izoneheight) AS INTEGER)
       AND decl BETWEEN idecl_min 
                    AND idecl_max
  ;

END;

