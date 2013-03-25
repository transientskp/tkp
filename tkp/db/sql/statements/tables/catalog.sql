CREATE TABLE catalog 
  (id SERIAL
  ,"name" VARCHAR(50) NOT NULL
  ,fullname VARCHAR(250) NOT NULL
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  )
;
