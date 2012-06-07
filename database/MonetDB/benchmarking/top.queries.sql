-------------------------------- (0) ----------------------------------
/* Loading the "fixed" catalog data into the database
 * with scripts
 */
/* COPY INTO FROM file */
mclient < load.cat.nvss.sql /* 1.7M records)*/
mclient < load.cat.wenss.sql /* 220k record */
...

-------------------------------- (1) ----------------------------------
/* INSERT INTO datasets 
 * We use a function to retrieve the seq. id needed for further processing
 */
SELECT insertDataset('description for dataset/observation');

-------------------------------- (2) ----------------------------------
/* INSERT INTO images
 * We use a function to retrieve the seq. id needed for further processing
 * images contains (meta-) data about an image
 */
SELECT insertImage(ds_id,timestamp,tau,...);

-------------------------------- (3) ----------------------------------
/* After every image is processed the extracted sources and its 
 * parameter will be inserted into the "pipeline" database
 */
/* INSERT INTO extractedsources */
CALL InsertSrc(image_id,ra,decl,...)

-------------------------------- (4) ----------------------------------
/* Just inserted sources (in extractedsources) will be searched for 
 * associations (by comparings positions) in the (I) other images belonging 
 * to same dataset as this the current, and (II) in the assocxtrsources table
 * (where the associated sources are collected)
 */
/* INSERT INTO assocxtrsources*/
CALL AssocXSources2XSourcesByImage(image_id)

-------------------------------- (5) ----------------------------------
/* Same as (above) but now to cataloged sources */
CALL AssocXSources2CatByZones(mage_id)

