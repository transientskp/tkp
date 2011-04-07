DROP FUNCTION IF EXISTS fTestWhen;

DELIMITER //

CREATE FUNCTION fTestWhen(N INT) RETURNS VARCHAR(10) 
DETERMINISTIC 
BEGIN

  DECLARE res VARCHAR(10);

  CASE 
    WHEN N = 1 THEN
      SET res = 'een';
    WHEN (N = 2 OR N = 3) THEN
      SET res = '2or3';
    WHEN N = 4 THEN
      SET res = 'vier';
    ELSE
      SET res = '0>N>4';
  END CASE;
  
  RETURN res;

END;
//

DELIMITER ;
