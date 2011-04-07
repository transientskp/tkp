/*
 * This script test the assoc procedure in 
 * time as well as in frequency.
 */
SELECT insertdataset('assoc time+freq; test I') INTO @dsid;

-- image 1, t = 0, band = 1 
SELECT insertimage(@dsid, 1, 30000000, '/this/is/fake/data') INTO @image_id;
CALL assocsrc(@image_id,1.28,1.25,0.1,0.1, 10,1,10,1,10);
CALL assocsrc(@image_id,1.19,0.97,0.1,0.1, 10,1,10,1,10);
CALL assocsrc(@image_id,0.96,0.85,0.1,0.1, 10,1,10,1,10);
CALL assocsrc(@image_id,0.96,1.15,0.1,0.1, 10,1,10,1,10);
SELECT CONCAT(CONCAT('image ', @image_id), ' done') AS '';

-- image 2, t = 0, band = 4
SELECT insertimage(@dsid, 4, 42000000, '/this/is/fake/data') INTO @image_id;
CALL assocsrc(@image_id,1.28,1.25,0.1,0.1, 10,1,10,1,10);
CALL assocsrc(@image_id,1.19,0.97,0.1,0.1, 10,1,10,1,10);
CALL assocsrc(@image_id,0.96,0.85,0.1,0.1, 10,1,10,1,10);
CALL assocsrc(@image_id,0.96,1.15,0.1,0.1, 10,1,10,1,10);
SELECT CONCAT(CONCAT('image ', @image_id), ' done') AS '';

-- image 3, t = 1, band = 1 
SELECT insertimage(@dsid, 1, 30000000, '/this/is/fake/dataalso') INTO @image_id;
CALL assocsrc(@image_id,1.21,1.07,0.135,0.135, 10,1,10,1,10);
CALL assocsrc(@image_id,0.865,1.1,0.135,0.135, 10,1,10,1,10);
SELECT CONCAT(CONCAT('image ', @image_id), ' done') AS '';

-- image 4, t = 1, band = 4 
SELECT insertimage(@dsid, 4, 42000000, '/this/is/fake/dataalso') INTO @image_id;
CALL assocsrc(@image_id,1.21,1.07,0.135,0.135, 10,1,10,1,10);
CALL assocsrc(@image_id,0.865,1.1,0.135,0.135, 10,1,10,1,10);
SELECT CONCAT(CONCAT('image ', @image_id), ' done') AS '';

-- image 5, t = 2, band = 1 
SELECT insertimage(@dsid, 1, 30000000, '/this/is/also/fake/data') INTO @image_id;
CALL assocsrc(@image_id,1.0,1.0,.15,.125, 10,1,10,1,10);
SELECT CONCAT(CONCAT('image ', @image_id), ' done') AS '';

-- image 6, t = 2, band = 4 
SELECT insertimage(@dsid, 4, 42000000, '/this/is/also/fake/data') INTO @image_id;
CALL assocsrc(@image_id,1.0,1.0,.15,.125, 10,1,10,1,10);
SELECT CONCAT(CONCAT('image ', @image_id), ' done') AS '';

SELECT CONCAT(CONCAT('processing dataset ', @dsid), ' ready') AS '';

SELECT NOW() AS '';

SELECT a.id
      ,a.xtrsrc_id
      ,band
      ,seq_nr
      ,a.src_type
      ,a.assoc_xtrsrcid 
  FROM associatedsources a
      ,extractedsources
      ,images e 
 WHERE a.xtrsrc_id = xtrsrcid 
   AND image_id = imageid 
   AND ds_id = @dsid
--   AND src_type = 'X'
ORDER BY a.id;

SELECT NOW() AS '';

SELECT a.id
      ,a.xtrsrc_id
      ,band
      ,seq_nr
      ,a.src_type
      ,a.assoc_xtrsrcid 
  FROM associatedsources a
      ,extractedsources
      ,images e 
 WHERE a.xtrsrc_id = xtrsrcid 
   AND image_id = imageid 
   AND ds_id = @dsid
   AND src_type = 'X'
ORDER BY a.id;
