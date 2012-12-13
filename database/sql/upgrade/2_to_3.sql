UPDATE version SET value=3 WHERE name='revision'; %SPLIT%

CREATE TABLE rejectreason (
	id INT AUTO_INCREMENT,
	description VARCHAR(512),
	PRIMARY KEY (id)
); %SPLIT%

CREATE TABLE rejection (
   id INT AUTO_INCREMENT,
   image INT,
   rejectreason INT,
   comment VARCHAR(512),
   PRIMARY KEY (id),
   FOREIGN KEY (image) REFERENCES image(id),
   FOREIGN KEY (rejectreason) REFERENCES rejectreason(id)
); %SPLIT%

