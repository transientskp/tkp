CREATE TABLE rejectreason
  (id SERIAL
	,description VARCHAR(512)
{% ifdb postgresql %}
	,PRIMARY KEY (id)
{% endifdb %}
);

INSERT INTO rejectreason VALUES (0, 'RMS too high');
INSERT INTO rejectreason VALUES (1, 'beam invalid');
INSERT INTO rejectreason VALUES (2, 'bright source near');