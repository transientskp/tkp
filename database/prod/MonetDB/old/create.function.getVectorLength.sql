--DROP FUNCTION getVectorLength;

CREATE FUNCTION getVectorLength(v1 DOUBLE
                               ,v2 DOUBLE
                               ,v3 DOUBLE
                               ) RETURNS DOUBLE 
BEGIN
  
  RETURN SQRT(POWER(v1, 2) + POWER(v2, 2) + POWER(v3, 2));

END;
