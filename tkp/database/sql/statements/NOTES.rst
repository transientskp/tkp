
Notes about SQL dialects
========================

* When a table has a SERIAL column, it is automatically also a primary key in
  the case of MonetDB. For PostgreSQL it is not.

* PostgreSQL doesn't understand DOUBLE, only DOUBLE PRECISION

* declaring something auto increment works different in monetdb and postgresql.
  it is probably just better to declare a column as type SERIAL.

* The syntax for declaring functions differs significantly

* When using a function, for MonetDB the DECLARE statements need to be between
  the BEGIN END statements, for PostgreSQL  _before_ the statements.

* PostgreSQL has a lastval() function that returns the last inserted ID. For
  MonetDB you need to get the nextval of the sequency manually.

* postgresql(9) only support procedural code inside a DO statement. If version8
  you need to use a function and call that.

 * Variable assigment for monetDB is SET bla = 'bla'. For PostgreSQL it is
  bla := 'bla'. PostgreSQL can only do this inside a function or inside a DO
  block.