--DROP FUNCTION cartesian;

/**
 * This function computes the x,y,z co-ordinates on the cartesian unit sphere 
 * for a given ra, decl.
 * ra and decl are both in degrees.
 */
CREATE FUNCTION cartesian(ira DOUBLE PRECISION, idecl DOUBLE PRECISION)
RETURNS TABLE (x DOUBLE PRECISION, y DOUBLE PRECISION, z DOUBLE PRECISION)


{% ifdb postgresql %}
AS $$
  SELECT  COS(RADIANS($2)) * COS(RADIANS($1)) AS x
         ,COS(RADIANS($2)) * SIN(RADIANS($1)) AS y
         ,SIN(RADIANS($2)) AS z;
         ;
$$ LANGUAGE SQL;
{% endifdb %}
