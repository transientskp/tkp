DELETE FROM multiplecatalogassocs;
ALTER TABLE multiplecatalogassocs AUTO_INCREMENT = 1;

DELETE FROM multiplecatalogsources;
ALTER TABLE multiplecatalogsources AUTO_INCREMENT = 1;

CALL MultipleCatMatchingInit();


