CREATE TABLE rejectreason
  (id SERIAL
	,description VARCHAR(512)
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
);

INSERT INTO rejectreason VALUES (0, 'RMS invalid');
INSERT INTO rejectreason VALUES (1, 'beam invalid');
INSERT INTO rejectreason VALUES (2, 'bright source near');
INSERT INTO rejectreason VALUES (3, 'tau_time invalid');
INSERT INTO rejectreason VALUES (4, 'contains NaN');
