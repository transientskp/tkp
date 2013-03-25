{% ifdb monetdb %}
CREATE SEQUENCE seq_frequencyband AS SMALLINT;
CREATE TABLE frequencyband
  (id SMALLINT NOT NULL DEFAULT NEXT VALUE FOR seq_frequencyband
{% endifdb %}

{% ifdb postgresql %}
CREATE TABLE frequencyband
  (id SERIAL
{% endifdb %}

  ,freq_central DOUBLE PRECISION DEFAULT NULL
  ,freq_low DOUBLE PRECISION DEFAULT NULL
  ,freq_high DOUBLE PRECISION DEFAULT NULL
  ,PRIMARY KEY (id)
  )
;

