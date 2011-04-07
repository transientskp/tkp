SET @wenss = 1000;

SELECT NOW() AS 'Deleting wenss sources';

SELECT '';

DELETE
  FROM catalogedsources
 WHERE cat_id = 3
   AND orig_catsrcid > @wenss
;

SELECT NOW() AS 'Calling AssocCatSrcs()';

SELECT '';

CALL AssocCatSrcs();

SELECT NOW() AS 'Result';

SELECT '';

SELECT COUNT(*)
  FROM associatedcatsources
;

SELECT NOW() AS 'Ready';

