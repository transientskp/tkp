--DROP FUNCTION degrees;

/**
 */
CREATE FUNCTION degrees(r double precision) RETURNS double precision AS $$
BEGIN
    RETURN r * 180 / PI();
END;
$$ language plpgsql;
