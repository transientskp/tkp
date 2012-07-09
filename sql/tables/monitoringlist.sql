/* TODO: maybe add this?:
,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
*/

CREATE TABLE monitoringlist
  (id INTEGER AUTO_INCREMENT
  ,xtrsrc INTEGER
  ,ra DOUBLE DEFAULT 0
  ,decl DOUBLE DEFAULT 0
  ,ds_id INTEGER NOT NULL
  ,userentry BOOLEAN DEFAULT FALSE
  ,PRIMARY KEY (id)

  )
;
