DROP PROCEDURE IF EXISTS AssocXSource;

DELIMITER //

/*+------------------------------------------------------------------+
 *| This procedure                                                   |
 *| (1) adds an extracted source to the extractedsources table.      |
 *| (2) tries to associate the source with sources previously        |
 *|     detected for this data set (same ds_id)                      |
 *| (3) also tries to associate the source with cataloged sources    |
 *| (4) If found, an association will be added to the                |
 *|     associatedsources table.                                     |
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
CREATE PROCEDURE AssocXSource(IN ixtrsrcid INT
                             /*,IN icatname VARCHAR(50)*/
                             )
BEGIN

  DECLARE icatname VARCHAR(50);
  DECLARE izone INT;
  DECLARE ira, idecl, ira_err, idecl_err, ix, iy, iz DOUBLE;
  DECLARE izoneheight, itheta, isintheta, ialpha DOUBLE;

  SET icatname = "WENSS";

  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;

  SET itheta = 1; /* in degrees */

  SELECT ra
        ,decl
        ,ra_err
        ,decl_err
        ,x
        ,y
        ,z
    INTO ira
        ,idecl
        ,ira_err
        ,idecl_err
        ,ix
        ,iy
        ,iz
    FROM extractedsources
   WHERE xtrsrcid = ixtrsrcid
  ;
 
  SET ialpha = alpha(itheta, idecl);
  SET isintheta = SIN(RADIANS(itheta));

  INSERT INTO associatedsources
    (xtrsrc_id
    ,assoc_type
    ,assoc_catsrc_id
    ,assoc_weight
    ,assoc_distance_arcsec
    )
    SELECT ixtrsrcid
          ,'X'
          ,catsrcid
          ,getWeightRectIntersection(ra,decl,ra_err,decl_err,ira,idecl,ira_err,idecl_err) AS assoc_weight
          ,getDistanceArcsec(ra,decl,ira,idecl) AS assoc_distance_arcsec
      FROM catalogedsources
          ,catalogs
     WHERE cat_id = catid
      AND catname = icatname
      AND zone BETWEEN FLOOR((idecl - itheta) / izoneheight)
                   AND FLOOR((idecl + itheta) / izoneheight)
      AND ra BETWEEN ira - ialpha
                 AND ira + ialpha
      AND decl BETWEEN idecl - itheta
                   AND idecl + itheta
      AND isintheta > SIN(2 * ASIN(SQRT(POWER(x - ix, 2) + POWER(y - iy, 2) + POWER(z - iz, 2)) / 2))
      AND doSourcesIntersect(ra,decl,ra_err,decl_err,ira,idecl,ira_err,idecl_err)
    ORDER BY assoc_weight DESC
            ,assoc_distance_arcsec
  ;

END;
//

DELIMITER ;

