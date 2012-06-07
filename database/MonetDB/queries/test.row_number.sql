create table tt (
  id int,
  var varchar(12)
);

insert into tt (id, var) values (1,'een'),(2,'twee'),(3,'drie'),(4,'vier');

select row_number() over()
  from tt
;

--drop table tt;
