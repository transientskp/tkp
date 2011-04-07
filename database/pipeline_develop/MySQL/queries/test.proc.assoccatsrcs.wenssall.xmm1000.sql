SET @xmm = 1000;

SELECT NOW() AS 'Deleting xmm sources';

SELECT '';

DELETE
  FROM catalogedsources
 WHERE cat_id = 4
   AND orig_catsrcid > @xmm
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

