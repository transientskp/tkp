/**
 * This table stores the information about the catalogs that are
 * loaded into the pipeline database.
 */

CREATE TABLE catalog 
  (id TINYINT AUTO_INCREMENT
  ,"name" VARCHAR(50) NOT NULL
  ,fullname VARCHAR(250) NOT NULL
  ,PRIMARY KEY (id)
);
