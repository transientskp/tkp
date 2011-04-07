SET @wenss = 1000;
SET @xmm = 1000;

SELECT NOW() AS 'Deleting wenss sources';

SELECT '';

DELETE
  FROM catalogedsources
 WHERE cat_id = 3
   AND orig_catsrcid > @wenss
;

SELECT NOW() AS 'Deleting xmm A sources';

SELECT '';

DELETE
  FROM catalogedsources
 WHERE cat_id = 4
   AND orig_catsrcid > @xmm
;

SELECT NOW() AS 'Deleting xmm B sources';

SELECT '';

DELETE
  FROM catalogedsources
 WHERE cat_id = 5
   AND orig_catsrcid > @xmm
;

SELECT NOW() AS 'Calling AssocCatSrcs()';

SELECT '';

CALL AssocCatSrcs();

SELECT NOW() AS 'Result';

SELECT '';

SELECT c1.cat_id
      ,catsrc_id
      ,c1.ra
      ,c1.decl
      ,c2.cat_id
      ,assoc_catsrcid
      ,c2.ra
      ,c2.decl
  FROM associatedcatsources a
      ,catalogedsources c1
      ,catalogedsources c2 
 WHERE a.catsrc_id = c1.catsrcid 
   AND a.assoc_catsrcid = c2.catsrcid
ORDER BY id
;

SELECT COUNT(*)
  FROM associatedcatsources
;

SELECT NOW() AS 'Ready';

