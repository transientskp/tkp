--DROP FUNCTION getDistanceArcsec;

/**
 * This function calculates the distance between two point sources.
 * Input ra and decl are in sys.sys.degrees
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

  SET cosd = COS(RADIANS(idecl1));
  SET u1 = COS(RADIANS(idecl1)) * COS(RADIANS(ira1));
  SET u2 = COS(RADIANS(idecl1)) * SIN(RADIANS(ira1));
  SET u3 = SIN(RADIANS(idecl1));

  SET cosd = COS(RADIANS(idecl2));
  SET v1 = COS(RADIANS(idecl2)) * COS(RADIANS(ira2));
  SET v2 = COS(RADIANS(idecl2)) * SIN(RADIANS(ira2));
  SET v3 = SIN(RADIANS(idecl2));
  
  /*SET d1 = COS(RADIANS(idecl2)) * COS(RADIANS(ira2)) - COS(RADIANS(idecl1)) * COS(RADIANS(ira1));
  SET d2 = COS(RADIANS(idecl2)) * SIN(RADIANS(ira2)) - COS(RADIANS(idecl1)) * SIN(RADIANS(ira1));
  SET d3 = SIN(RADIANS(idecl2)) - SIN(RADIANS(idecl1));*/
  /*SET resu = d1+d2+d3;*/
  
  /*RETURN d1 + d2 + d3;*/
  /*RETURN SQRT(POWER(d1, 2) + POWER(d2, 2) + POWER(d3, 2));incorrect result*/
  /*RETURN 3600 * degrees(2 * ASIN(getVectorLength(v1 - u1, v2 - u2, v3 - u3) / 2));*/
  RETURN 3600 * DEGREES(2 * ASIN(SQRT((u1 - v1) * (u1 - v1) + (u2 - v2) * (u2 - v2) + (u3 - v3) * (u3 - v3)) / 2));
  /*RETURN resu;*/
  
END;
