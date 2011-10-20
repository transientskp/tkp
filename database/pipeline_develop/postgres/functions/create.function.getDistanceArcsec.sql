--DROP FUNCTION getDistanceArcsec;

/**
 * This function calculates the distance between two point sources.
 * Input ra and decl are in sys.sys.degrees
 * Output distance is in arcsec.
 */
CREATE FUNCTION getDistanceArcsec(ira1 double precision
                                 ,idecl1 double precision
                                 ,ira2 double precision
                                 ,idecl2 double precision
                                 ) RETURNS double precision as $$

DECLARE cosd double precision;
declare u1 double precision;
declare u2 double precision;
declare u3 double precision;
declare v1 double precision;
declare v2 double precision;
declare v3 double precision;
DECLARE d1 double precision;
declare d2 double precision;
declare d3 double precision;
DECLARE resu double precision;
BEGIN

  cosd := COS(rad(idecl1));
  u1 := COS(rad(idecl1)) * COS(rad(ira1));
  u2 := COS(rad(idecl1)) * SIN(rad(ira1));
  u3 := SIN(rad(idecl1));

  cosd := COS(rad(idecl2));
  v1 := COS(rad(idecl2)) * COS(rad(ira2));
  v2 := COS(rad(idecl2)) * SIN(rad(ira2));
  v3 := SIN(rad(idecl2));
  
  /*d1 := COS(rad(idecl2)) * COS(rad(ira2)) - COS(rad(idecl1)) * COS(rad(ira1));
  d2 := COS(rad(idecl2)) * SIN(rad(ira2)) - COS(rad(idecl1)) * SIN(rad(ira1));
  d3 := SIN(rad(idecl2)) - SIN(rad(idecl1));*/
  /*resu := d1+d2+d3;*/
  
  /*RETURN d1 + d2 + d3;*/
  /*RETURN SQRT(POWER(d1, 2) + POWER(d2, 2) + POWER(d3, 2));incorrect result*/
  /*RETURN 3600 * degrees(2 * ASIN(getVectorLength(v1 - u1, v2 - u2, v3 - u3) / 2));*/
  RETURN 3600 * deg(2 * ASIN(SQRT((u1 - v1) * (u1 - v1) + (u2 - v2) * (u2 - v2) + (u3 - v3) * (u3 - v3)) / 2));
  /*RETURN resu;*/
  
END;
$$ language plpgsql;
