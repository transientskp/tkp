CREATE TABLE rejectreason
  (id SERIAL
	,description VARCHAR(512)
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
);

INSERT INTO rejectreason (description) VALUES ('RMS invalid');
INSERT INTO rejectreason (description) VALUES ('beam invalid');
INSERT INTO rejectreason (description) VALUES ('bright source near');
INSERT INTO rejectreason (description) VALUES ('tau_time invalid');
