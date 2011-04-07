DELETE FROM assoccatsources;
ALTER SEQUENCE seq_assoccatsources RESTART WITH 1;
DELETE FROM assocxtrsources;
ALTER SEQUENCE seq_assocxtrsources RESTART WITH 1;
DELETE FROM associatedsources;
ALTER SEQUENCE seq_associatedsources RESTART WITH 1;
DELETE FROM extractedsources;
ALTER SEQUENCE seq_extractedsources RESTART WITH 1;
DELETE FROM images;
ALTER SEQUENCE seq_images RESTART WITH 1;
DELETE FROM datasets;
ALTER SEQUENCE seq_datasets RESTART WITH 1;

