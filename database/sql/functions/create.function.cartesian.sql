--DROP FUNCTION cartesian;

/**
 * This function computes the x,y,z co-ordinates on the cartesian unit sphere 
 * for a given ra, decl.
 * ra and decl are both in degrees.
 */
CREATE FUNCTION cartesian(ira DOUBLE
                         ,idecl DOUBLE
                         ) RETURNS TABLE (x DOUBLE
                                         ,y DOUBLE
                                         ,z DOUBLE
                                          )
BEGIN
  RETURN TABLE (
     SELECT  COS(RADIANS(idecl))*COS(RADIANS(ira)) AS x
            ,COS(RADIANS(idecl))*SIN(RADIANS(ira)) AS y
            ,SIN(RADIANS(idecl)) AS z
           )
           ;
END;
