--DROP FUNCTION radians;

/**
 */
CREATE FUNCTION radians(d double precision) RETURNS double precision as $$
BEGIN
    RETURN d * PI() / 180;
END;
$$ language plpgsql;
