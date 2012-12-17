CREATE TABLE rejectreason (
	id INT AUTO_INCREMENT,
	description VARCHAR(512),
	PRIMARY KEY (id)
);

INSERT INTO rejectreason VALUES (0, 'RMS too high');
INSERT INTO rejectreason VALUES (1, 'beam invalid');
INSERT INTO rejectreason VALUES (2, 'bright source near');