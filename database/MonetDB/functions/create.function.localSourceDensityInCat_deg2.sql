--DROP FUNCTION localSourceDensityInCat_deg2;

/*
 * This function returns the local source density in the neighborhood
 * of the specified source (ixtrsrcid).
 * The neighborhood (area) is determined by itheta [degrees], 
 * which sets the radius centred at ixtrsrcid. 
 * The curved surface area of the neighborhood (spherical cap)
 * is in degrees squared.
 * The number of sources in the specified catalog (icatname) in 
 * the neighborhood determine the source density [deg^{-2}].
 */
CREATE FUNCTION localSourceDensityInCat_deg2(icatname VARCHAR(50)
                                            ,itheta DOUBLE
                                           ,ixtrsrcid INT
                                           ) RETURNS DOUBLE
BEGIN
  
  DECLARE ncatsources INT;
  DECLARE izoneheight, caparea DOUBLE;

  /* itheta determines the radius of the area (with the ixtrsrcid source 
   * at its centre. caparea is the curved surface area of the spherical cap
   */
  SET caparea = 64800 * (1 - COS(RADIANS(itheta))) / PI();

  /*TODO
  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;*/
  SET izoneheight = 1;

  SELECT COUNT(*)
    INTO ncatsources
    FROM extractedsources x1
        ,catalogedsources c1
        ,catalogs c0
   WHERE c1.cat_id = c0.catid
     AND c0.catname = UPPER(icatname)
     AND x1.xtrsrcid = ixtrsrcid
     AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
     AND c1.zone BETWEEN FLOOR((x1.decl - itheta) / izoneheight)
                     AND FLOOR((x1.decl + itheta) / izoneheight)
     AND c1.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                   AND x1.ra + alpha(itheta, x1.decl)
     AND c1.decl BETWEEN x1.decl - itheta
                     AND x1.decl + itheta
  ;

  RETURN ncatsources / caparea ;

END;


