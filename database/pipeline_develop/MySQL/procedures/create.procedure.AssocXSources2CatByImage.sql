DROP PROCEDURE IF EXISTS AssocXSources2CatByImage;

DELIMITER //

/*+------------------------------------------------------------------+
 *| This procedure tries to associate extractedsources in an image   |
 *| (image_id = iimage_id) to previous extractedsources (these are   |
 *| already in the associatedsources.                                |
 *| Sources that could not be associated will be inserted in the     |
 *| associatedsources table as well.                                 |
 *|                                                                  |
 *+------------------------------------------------------------------+
 *| Query is as follows:                                             |
 *| select == assocs ==                                              |
 *| union                                                            |
 *| select == no assocs for sources in current image ==              |
 *| union                                                            |
 *| select == no assocs in case of empty table ==                    |
 *| ;                                                                |
 *|                                                                  |
 *| Select 1:                                                        |
 *| sources with assocs                                              |
 *| Select 2:                                                        |
 *| Query to select new sources in current image i.e. no associations| 
 *| could be found in associatedsources (or: all sources from        |
 *| image_id = iimageid that do NOT intersect with sources from      |
 *| images with the same ds_id as iimageid).                         |
 *| Select 3:                                                        |
 *| Select the sources that could not be associated, because the     |
 *| associatedsources table is empty.                                |
 *|                                                                  |
 *+------------------------------------------------------------------+
 *|                         Bart Scheers                             |
 *|                          2009-10-28                              |
 *|                  University of Amsterdam                         |
 *|                      LOFAR TKP Project                           |
 *+------------------------------------------------------------------+
 *| TODO:                                                            |
 *+------------------------------------------------------------------+
 *| Open questions:                                                  |
 *+------------------------------------------------------------------+
 */
CREATE PROCEDURE AssocXSources2CatByImage(IN iimageid INT)

BEGIN

  DECLARE izoneheight, itheta, N_density DOUBLE;
  
  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  SET itheta = 1;
  SET N_density = 60;

  INSERT INTO assoccatsources
    (xtrsrc_id
    ,assoc_catsrc_id
    ,assoc_weight
    ,assoc_distance_arcsec
    ,assoc_r
    ,assoc_prob
    )
    SELECT t.xtrsrc_id
          ,CASE WHEN t.assoc_catsrc_id = 0
                THEN NULL
                ELSE t.assoc_catsrc_id
           END
          ,t.assoc_weight
          ,t.assoc_distance_degrees * 3600
          ,t.assoc_r
          ,EXP(-PI() * t.assoc_distance_degrees * t.assoc_distance_degrees * N_density)
      FROM (SELECT x1.xtrsrcid AS xtrsrc_id
                  ,c1.catsrcid AS assoc_catsrc_id
                  ,getWeightRectIntersection(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                            ,c1.ra,c1.decl,c1.ra_err,c1.decl_err
                                            ) AS assoc_weight
                  ,DEGREES(2 * ASIN(SQRT(POWER((COS(radians(c1.decl)) * COS(radians(c1.ra))
                                               - COS(radians(x1.decl)) * COS(radians(x1.ra))
                                               ), 2)
                                        + POWER((COS(radians(c1.decl)) * SIN(radians(c1.ra))
                                                - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                                                ), 2)
                                        + POWER((SIN(radians(c1.decl))
                                                - SIN(radians(x1.decl))
                                                ), 2)
                                        ) / 2)
                          ) AS assoc_distance_degrees
                  ,SQRT( (x1.ra - c1.ra) * (x1.ra - c1.ra)
                         / (( (x1.ra - (x1.ra + c1.ra) / 2) * (x1.ra - (x1.ra + c1.ra) / 2)
                            + (c1.ra - (x1.ra + c1.ra) / 2) * (c1.ra - (x1.ra + c1.ra) / 2)
                            ) / 2)
                       + (x1.decl - c1.decl) * (x1.decl - c1.decl)
                         / (( (x1.decl - (x1.decl + c1.decl) / 2) * (x1.decl - (x1.decl + c1.decl) / 2)
                            + (c1.decl - (x1.decl + c1.decl) / 2) * (c1.decl - (x1.decl + c1.decl) / 2)
                            ) / 2)
                       ) AS assoc_r
              FROM extractedsources x1
                  ,catalogedsources c1
                  ,catalogs c
             WHERE x1.image_id = iimageid
               AND c1.cat_id = c.catid
               AND c1.zone BETWEEN FLOOR((x1.decl - itheta) / izoneheight)
                               AND FLOOR((x1.decl + itheta) / izoneheight)
               AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                             AND x1.ra + alpha(itheta,x1.decl)
               AND c1.decl BETWEEN x1.decl - itheta
                               AND x1.decl + itheta
               /*AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                     ,c1.ra,c1.decl,c1.ra_err,c1.decl_err)*/
               AND doPosErrCirclesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                           ,c1.ra,c1.decl,c1.ra_err,c1.decl_err)
           ) t
  ;

END;
//

DELIMITER ;

