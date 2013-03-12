
Notes about SQL dialects
========================

* When a table has a SERIAL column, it is automatically also a primary key in
  the case of MonetDB. For PostgreSQL it is not.

* PostgreSQL doesn't understand DOUBLE, only DOUBLE PRECISION

* declaring something auto increment works different in monetdb and postgresql.
  it is probably just better to declare a column as type SERIAL.
