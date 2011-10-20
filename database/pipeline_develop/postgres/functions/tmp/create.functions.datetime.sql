DROP FUNCTION IF EXISTS getYear;

DELIMITER //

/**
 * The input argument must be a BIGINT, and in the
 * timestamp format:
 * YYYYMMDDHHmmSSmmm
 * f.ex. 20081223135723967 is
 * december 23rd 2008, 13:57:23, 967 milliseconds
 */
CREATE FUNCTION getYear(itimestamp BIGINT
                       ) RETURNS INT $$ language plpgsql;
DETERMINISTIC

BEGIN
  RETURN FLOOR(itimestamp / 10000000000000);

END;
$$ language plpgsql;
