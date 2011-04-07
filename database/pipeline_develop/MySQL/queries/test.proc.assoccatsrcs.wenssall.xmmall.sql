SELECT NOW() AS 'Calling AssocCatSrcs()';

SELECT '';

CALL AssocCatSrcs();

SELECT NOW() AS 'Result';

SELECT '';

SELECT COUNT(*)
  FROM associatedcatsources
;

SELECT NOW() AS 'Ready';

