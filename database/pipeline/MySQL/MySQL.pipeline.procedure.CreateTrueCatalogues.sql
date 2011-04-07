USE pipeline;

DROP PROCEDURE IF EXISTS CreateTrueCatalogues;

DELIMITER //

CREATE PROCEDURE CreateTrueCatalogues()

BEGIN

  DECLARE i INT DEFAULT 0;

  WHILE i < 1000 DO
    INSERT INTO catalogues
      (catid
      ,catname
      ,fullname
    ) VALUES
      (i + 1001
      ,CONCAT('TC FPOS7.5', ':', i + 1)
      ,CONCAT('True Catalogue 1000 FPOS7.5', ':', 'ONESOURCEOFFS', i, '.FITS')
    )
    ;
    SET i = i + 1;
  END WHILE;

END;
//

DELIMITER ;
