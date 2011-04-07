--DROP FUNCTION getDistanceArcsec;

/**
 * This function calculates the distance between two point sources.
 * Input ra and decl are in degrees
 * Output distance is in arcsec.
 */
CREATE FUNCTION getDistanceArcsec(ira1 DOUBLE
                                 ,idecl1 DOUBLE
                                 ,ira2 DOUBLE
                                 ,idecl2 DOUBLE
                                 ) RETURNS DOUBLE 
BEGIN

  DECLARE cosd, u1, u2, u3, v1, v2, v3 DOUBLE;
  DECLARE d1, d2, d3 DOUBLE;
  DECLARE resu DOUBLE;

  SET cosd = COS(radians(idecl1));
  SET u1 = COS(radians(idecl1)) * COS(radians(ira1));
  SET u2 = COS(radians(idecl1)) * SIN(radians(ira1));
  SET u3 = SIN(radians(idecl1));

  SET cosd = COS(radians(idecl2));
  SET v1 = COS(radians(idecl2)) * COS(radians(ira2));
  SET v2 = COS(radians(idecl2)) * SIN(radians(ira2));
  SET v3 = SIN(radians(idecl2));
  
  /*SET d1 = COS(radians(idecl2)) * COS(radians(ira2)) - COS(radians(idecl1)) * COS(radians(ira1));
  SET d2 = COS(radians(idecl2)) * SIN(radians(ira2)) - COS(radians(idecl1)) * SIN(radians(ira1));
  SET d3 = SIN(radians(idecl2)) - SIN(radians(idecl1));*/
  /*SET resu = d1+d2+d3;*/
  
  /*RETURN d1 + d2 + d3;*/
  /*RETURN SQRT(POWER(d1, 2) + POWER(d2, 2) + POWER(d3, 2));incorrect result*/
  /*RETURN 3600 * degrees(2 * ASIN(getVectorLength(v1 - u1, v2 - u2, v3 - u3) / 2));*/
  RETURN 3600 * DEGREES(2 * ASIN(SQRT((u1 - v1) * (u1 - v1) + (u2 - v2) * (u2 - v2) + (u3 - v3) * (u3 - v3)) / 2));
  /*RETURN resu;*/
  
END;
