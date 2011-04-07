drop table if exists t;

create table t (
  id int
) engine=innodb;

drop table if exists tt;

create table tt (
  id int,
  cnt int
) engine=innodb;

insert into t values (1),(2),(3),(4),(5);

set @cnt = 0;
select id
      ,@cnt := @cnt + 1
  from t
 where id > 3
;

set @cnt = 0;
insert into tt
  select id
        ,@cnt := @cnt + 1
    from t
   where id > 3
;

select * from tt;

delete from tt;

drop procedure if exists pr;

delimiter //

create procedure pr()
begin

  set @ncnt = 0;

  insert into tt
    select id
          ,@ncnt := @ncnt + 1
      from t
     where id > 3
  ;

end;
//

delimiter ;

call pr();

select * from t;

select * from tt;

