DROP FUNCTION IF EXISTS testNull;

DELIMITER //

CREATE FUNCTION testNull(x DOUBLE
                        ,y DOUBLE
                        ,z DOUBLE
                        ) RETURNS DOUBLE
DETERMINISTIC

BEGIN

  IF z IS NULL THEN
    RETURN x;
  ELSE
    RETURN y;
  END IF;

END;
//

DELIMITER ;
