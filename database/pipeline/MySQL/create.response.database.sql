/* TEST CODE
 * JDS, 29 Sept 2008
 *
 * Tables for holding work packages and tasks serialised from the response
 * handling part of the pipeline.
 */

USE pipeline_testing;

CREATE TABLE workpackages (
  wp_id INT NOT NULL AUTO_INCREMENT,
  lc_id INT NOT NULL,
  FOREIGN KEY (lc_id) REFERENCES extractedsources(assoc_xtrsrcid),
  description VARCHAR(100) NOT NULL,
  priority INT NOT NULL,
  submit_time DATETIME NOT NULL,
  finish_time DATETIME NULL,
  status ENUM("Pending", "Manager", "Cancelled", "Complete", "Aborted") NOT NULL DEFAULT "Pending",
  PRIMARY KEY(wp_id)
) ENGINE=InnoDB;

CREATE TABLE tasks (
  task_id INT NOT NULL AUTO_INCREMENT,
  wp_id INT NOT NULL,
  FOREIGN KEY (wp_id) REFERENCES workpackages(wp_id),
  description VARCHAR(100) NOT NULL,
  run_order INT NOT NULL,
  status ENUM("Pending", "Failed", "Complete", "Reverted") NOT NULL DEFAULT "Pending",
  finish_time DATETIME NULL,
  content BLOB NOT NULL,
  PRIMARY KEY(task_id)
) ENGINE=InnoDB;

DELIMITER //

CREATE FUNCTION InsertWorkPackage(ilc_id INT
                                 ,idescription VARCHAR(100)
                                 ,ipriority INT
                                 ) RETURNS INT
READS SQL DATA
BEGIN

  INSERT INTO workpackages
    (lc_id
    ,description
    ,priority
    ,submit_time
  ) VALUES
  (ilc_id
  ,idescription
  ,ipriority
  ,NOW()
  )
  ;

  RETURN LAST_INSERT_ID();

END;
//

CREATE PROCEDURE RetrieveWP(IN iwp_id INT
                           ,OUT olc_id INT
                           ,OUT opriority INT
                           ,OUT owp_id INT
                           ,OUT osubmit_time DATETIME
                           ,OUT ofinish_time DATETIME
                           ,OUT ostatus ENUM("Pending", "Manager", "Cancelled", "Complete", "Aborted")
                           )
BEGIN
    
    UPDATE
        workpackages
    SET
        status = "Manager"
    WHERE
        wp_id = iwp_id
    AND
        status = "Pending";

    SELECT 
        lc_id, priority, wp_id, submit_time, finish_time, status 
    INTO
        olc_id, opriority, owp_id, osubmit_time, ofinish_time, ostatus 
    FROM 
        workpackages
    WHERE
        wp_id = iwp_id;

END;
//

