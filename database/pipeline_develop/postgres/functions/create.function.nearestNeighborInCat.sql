--DROP FUNCTION nearestNeighborInCat;

CREATE or replace FUNCTION nearestNeighborInCat(ira double precision
                                     ,idecl double precision
                                     ,icatname VARCHAR(50)
                                     ) RETURNS TABLE (catsrcid INT
                                                     ,catsrcname VARCHAR(120)
                                                     ,i_int double precision
                                                     ,distance_arcsec double precision
                                                     ) as $$
  DECLARE izoneheight double precision;
declare itheta double precision;
declare ix double precision;
declare iy double precision;
declare iz double precision;
BEGIN
  
  
  ix := COS(RAD(idecl)) * COS(RAD(ira));
  iy := COS(RAD(idecl)) * SIN(RAD(ira));
  iz := SIN(RAD(idecl));

  /* TODO: 
   * retrieve zoneheight from table ->
   * meaning add a columns to the table
  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;*/
  izoneheight := 1;
  itheta := 1;

  RETURN query
    SELECT catsrcid
          ,catsrcname
          ,i_int_avg
          ,3600 * DEG(2 * ASIN(SQRT((ix - c1.x) * (ix - c1.x)
                                       + (iy - c1.y) * (iy - c1.y)
                                       + (iz - c1.z) * (iz - c1.z)
                                       ) / 2) 
                         ) AS distance
      FROM catalogedsources c1
          ,catalogs c0
     WHERE c1.cat_id = c0.catid
       AND c0.catname = icatname
       AND c1.x * ix + c1.y * iy + c1.z * iz > COS(RAD(itheta))
       AND c1.zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                       AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
       AND c1.ra BETWEEN ira - alpha(itheta, idecl)
                     AND ira + alpha(itheta, idecl)
       AND c1.decl BETWEEN idecl - itheta
                       AND idecl + itheta
    ORDER BY distance ASC
    LIMIT 1
    ;

END
;
$$ language plpgsql;
