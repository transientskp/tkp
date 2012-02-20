/**
 * This table contains the different classes of associations that 
 * can be made. 
 * (See PROCEDURE InitObservation() for the values)
 * Note: This table has nothing to do with the classifictaion of the 
 * source (whether it is single or multiple f.ex.).
 */
CREATE TABLE associationclass (
  assoc_classid INT NOT NULL,
  type INT NOT NULL,
  assoc_class VARCHAR(10) DEFAULT NULL,
  description VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (assoc_classid)
);
