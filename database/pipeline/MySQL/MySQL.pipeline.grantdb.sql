USE mysql;

DELIMITER //

/**
 * This procedure initialises the pipeline database after it is created
 * successfully.
 */
CREATE PROCEDURE GrantDB(IN ihost VARCHAR(60)
                        ,IN idb VARCHAR(64)
                        ,IN iuser VARCHAR(16)
                        )
BEGIN

  INSERT INTO db
    (Host
    ,Db
    ,User
    ,Select_priv
    ,Insert_priv
    ,Update_priv
    ,Delete_priv
    ,Create_priv
    ,Drop_priv
    ,Grant_priv
    ,References_priv
    ,Index_priv
    ,Alter_priv
    ,Create_tmp_table_priv
    ,Lock_tables_priv
    ,Create_view_priv
    ,Show_view_priv
    ,Create_routine_priv
    ,Alter_routine_priv
    ,Execute_priv
    )
  VALUES
    (ihost
    ,idb
    ,iuser
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    ,'Y'
    )


  ;

END
//

DELIMITER ;
