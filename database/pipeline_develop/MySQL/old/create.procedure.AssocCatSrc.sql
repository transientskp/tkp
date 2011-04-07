DROP PROCEDURE IF EXISTS AssocCatSrc;

DELIMITER //

/*+------------------------------------------------------------------+
 *| This procedure                                                   |
 *+------------------------------------------------------------------+
 *| Input params:                                                    |
 *|   iimage_id  : the image_id from which this source was extracted |
 *|   ira        : RA of extracted source (in degrees)               |
 *|   idecl      : dec of extracted source (in degrees)              |
 *|   ira_err    : 1 sigma error on RA (in degrees)                  |
 *|   idecl_err  : 1 sigma error on dec (in degrees)                 |
 *|   iI_peak    : Peak flux of extracted source (in Jansky)         |
 *|   iI_peak_err: Error on peak flux of extracted source (in Jansky)|
 *|   iI_int     : Integrated flux of extracted source (in Jansky)   |
 *|   iI_int_err : Error on int. flux of extracted source (in Jansky)|
 *|   idet_sigma : The detection level of the extracted source       |
 *|                (in sigma)                                        |
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
CREATE PROCEDURE AssocCatSrc(IN icatsrcid INT
                            ,IN icat_id INT
                            ,IN ira DOUBLE
                            ,IN idecl DOUBLE
                            ,IN ira_err DOUBLE
                            ,IN idecl_err DOUBLE
                            ,IN ix DOUBLE
                            ,IN iy DOUBLE
                            ,IN iz DOUBLE
                            ,IN ii_peak_avg DOUBLE
                            ,IN ii_peak_avg_err DOUBLE
                            ,IN ii_int_avg DOUBLE
                            ,IN ii_int_avg_err DOUBLE
                            )
BEGIN

  DECLARE izoneheight DOUBLE;
  /* We might set theta lower than 1, because
   * we know with what catalogues we are dealing with
  DECLARE itheta DOUBLE DEFAULT 1;
  DECLARE sin_itheta DOUBLE;
  DECLARE ialpha DOUBLE;

  DECLARE icatsrcid INT DEFAULT NULL;
  DECLARE iassoc_catsrcid INT DEFAULT NULL;
  DECLARE nassoc_catsrcid INT DEFAULT 0;
  DECLARE iassoc_catsrcid INT DEFAULT NULL;
  DECLARE nassoc_catsrcid INT DEFAULT 0;
  DECLARE ifirst_catsrcid INT;

  DECLARE found BOOLEAN DEFAULT FALSE;
  DECLARE sigma INT DEFAULT 1;
  DECLARE iclass_id INT DEFAULT 0;
  DECLARE cat_class_id INT DEFAULT 0;
  DECLARE xtr_class_id INT DEFAULT 0;

  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;

  SET ialpha = alpha(itheta, idecl);
  SET sin_itheta = SIN(RADIANS(itheta));

  /* all the ids of associated sources
   */
  DROP TEMPORARY TABLE IF EXISTS assoccatsrcids;
  CREATE TEMPORARY TABLE assoccatsrcids (
    assoccatid INT,
    assoccatsrcid INT,
    UNIQUE INDEX (assoccatid
                 ,assoccatsrcid
                 )
  ) ENGINE = MEMORY
  ;

  /* Here we insert the associated ids into the temporary table. 
   * The SELECT query selects all the extractedsources in all the 
   * images that belong to the same dataset as to which the 
   * current image belongs to.
   */
  INSERT INTO assoccatsrcids
    SELECT cat_id AS assoccatid
          ,catsrcid AS assoccatsrcid
      FROM cataloguedsources
     WHERE cat_id > icat_id
       AND zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                    AND FLOOR((idecl + itheta)/izoneheight)
       AND ra BETWEEN ira - ialpha
                  AND ira + ialpha
       AND decl BETWEEN idecl - itheta
                    AND idecl + itheta
       /*
       AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
           POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
       */
       AND sin_itheta > SIN(2 * ASIN(SQRT(POW(x - ix, 2) + 
                                          POW(y - iy, 2) + 
                                          POW(z - iz, 2)) / 2))
       AND doIntersectElls(ira,idecl,ira_err,idecl_err
                          ,ra,decl,ra_err,decl_err)
    GROUP BY cat_id
  ;

  /* Here we select the previous associations of the associated sources 
   * of the current source.
   * It is necessary to do, because we want prevent the associations 
   * from wandering away. Therefore we further have to check if these 
   * can also be associated to the current source.
   */
  SELECT COUNT(*) 
    INTO nassoc_catsrcid
    FROM assoccatsrcids
  ;

  IF nassoc_catsrcid > 0 THEN
    INSERT INTO associatedcatsources
      (catsrc_id
      ,assoc_catsrcid
      )
      SELECT catsrc_id
            ,icatsrcid
        FROM associatedsources
            ,assoccatsrcids
            ,extractedsources 
     WHERE catsrc_id = catsrcid 
       AND assoccatsrcid = assoc_catsrcid 
       AND zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                    AND FLOOR((idecl + itheta)/izoneheight)
       AND ra BETWEEN ira - ialpha
                  AND ira + ialpha
       AND decl BETWEEN idecl - itheta
                    AND idecl + itheta
       /*
       AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
               POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
       */
       AND sin_itheta > SIN(2 * ASIN(SQRT(POW(x - ix, 2) + 
                                          POW(y - iy, 2) + 
                                          POW(z - iz, 2)) / 2))
       AND doIntersectElls(ira,idecl,ira_err,idecl_err
                          ,ra,decl,ra_err,decl_err)
    GROUP BY catsrc_id
    ;
  ELSE 
    INSERT INTO associatedcatsources
      (catsrc_id
      ,assoc_catsrcid
      )
    VALUES 
      (icatsrcid
      ,icatsrcid
      )
    ;
  END IF;

  DROP TEMPORARY TABLE IF EXISTS assoccatsrcids;

END;
//

DELIMITER ;

