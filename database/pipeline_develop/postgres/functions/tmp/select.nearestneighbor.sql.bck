declare izoneheight double precision;
declare ixtrsrcid INT;
declare itheta double precision;
declare icatname varchar(50);
set ixtrsrcid=41;
set izoneheight=1;
set itheta =1; 
set icatname='VLSS';


  SELECT c1.catsrcid
        ,3600 * DEGREES(2 * ASIN(SQRT((x1.x - c1.x) * (x1.x - c1.x)
                                     + (x1.y - c1.y) * (x1.y - c1.y) 
                                     + (x1.z - c1.z) * (x1.z - c1.z)
                                     ) / 2)) AS distance_arcsec
    FROM extractedsources x1
        ,catalogedsources c1
        ,catalogs c0
   WHERE c1.cat_id = c0.catid
     AND c0.catname = icatname
     AND x1.xtrsrcid = ixtrsrcid
     AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
     AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                     AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
     AND c1.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                   AND x1.ra + alpha(itheta, x1.decl)
     AND c1.decl BETWEEN x1.decl - itheta
                     AND x1.decl + itheta
  ORDER BY distance_arcsec 
  LIMIT 1
  ;


