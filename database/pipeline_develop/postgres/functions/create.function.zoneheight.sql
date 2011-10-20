--DROP FUNCTION zoneheight;

CREATE FUNCTION zoneheight() RETURNS double precision as $$
BEGIN
    
  RETURN 1.; 
END;
$$ language plpgsql;
