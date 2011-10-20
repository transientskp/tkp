--DROP PROCEDURE BuildZones;

/**
 * This procedure builds the zones table according to
 * the input zoneheight and theta (both in degrees).
 * ATTENTION:
 * The zone column in the extractedsources table will NOT be modified!
 * It is best to run this before an observation,
 * i.e. at initialisation time,
 * and when you have an idea about the zoneheight.
 * TODO: Find out what a good zoneheight will be.
 */
CREATE PROCEDURE BuildZones(izoneheight double precision)
BEGIN

  DECLARE maxZone INT;
  DECLARE minZone INT;
  DECLARE zones INT;

  DELETE FROM zoneheight;
  DELETE FROM zones;

  INSERT INTO zoneheight (zoneheight) VALUES (izoneheight); 

  SET maxZone = CAST(FLOOR((90.0 + izoneheight) / izoneheight) AS INTEGER);
  SET minZone = - maxZone;
  WHILE minZone < maxZone DO
    INSERT INTO zones 
    VALUES 
      (minZone
      ,minZone * izoneheight
      ,(minZone + 1) * izoneheight
      )
    ;
    SET minZone = minZone + 1;
  END WHILE;

END;
