DROP PROCEDURE IF EXISTS AssocXSourceByImage;

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
CREATE PROCEDURE AssocXSourceByImage(IN iimageid INT)

BEGIN

  INSERT INTO associatedsources
    (xtrsrc_id
    ,assoc_type
    ,assoc_xtrsrc_id
    ,assoc_weight
    ,assoc_distance_arcsec
    )
    SELECT x1.xtrsrcid AS xtrsrc_id
          ,'X' AS assoc_type
          ,x2.xtrsrcid AS assoc_xtrsrc_id
          ,getWeightRectIntersection(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                    ,x2.ra,x2.decl,x2.ra_err,x2.decl_err
                                    ) AS assoc_weight
          ,3600 * degrees(2 * ASIN(SQRT(POWER((COS(radians(x2.decl)) * COS(radians(x2.ra))
                                              - COS(radians(x1.decl)) * COS(radians(x1.ra))
                                              ), 2)
                                       + POWER((COS(radians(x2.decl)) * SIN(radians(x2.ra))
                                               - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                                               ), 2)
                                       + POWER((SIN(radians(x2.decl))
                                               - SIN(radians(x1.decl))
                                               ), 2)
                                       ) / 2)) AS assoc_distance_arcsec
      FROM extractedsources x1
          ,images
          ,datasets
          ,extractedsources x2
     WHERE x1.image_id = imageid
       AND ds_id = dsid
       AND dsid = (SELECT ds_id
                     FROM images
                    WHERE imageid = iimageid
                  )
       AND x1.image_id <> iimageid
       AND x2.image_id = iimageid
       AND dosourcesintersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                             ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
    ORDER BY assoc_weight DESC
            ,assoc_distance_arcsec
;

END;
//

DELIMITER ;

