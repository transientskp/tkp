SET SCHEMA pipeline;

DROP PROCEDURE TestCount;

CREATE PROCEDURE TestCount()
BEGIN

  DECLARE nassoc_catsrcid INT;

  SELECT COUNT(*)
    INTO nassoc_catsrcid
    FROM cataloguesources
   WHERE zone BETWEEN 30 AND 33
  ;

END;

