mysql> select id,xtrsrcid1,insert_src1,ra1,decl1,ra_err1,decl_err1,xtrsrcid2,insert_src2,ra2,decl2,ra_err2,decl_err2,'' as some_id,avg_ra,avg_decl from aux_associatedsources;
+----+-----------+-------------+------+-------+---------+-----------+-----------+-------------+-------+-------+---------+-----------+---------+--------+----------+
| id | xtrsrcid1 | insert_src1 | ra1  | decl1 | ra_err1 | decl_err1 | xtrsrcid2 | insert_src2 | ra2   | decl2 | ra_err2 | decl_err2 | some_id | avg_ra | avg_decl |
+----+-----------+-------------+------+-------+---------+-----------+-----------+-------------+-------+-------+---------+-----------+---------+--------+----------+
|  1 |         1 |           1 | 1.28 |  1.25 |     0.1 |       0.1 |         1 |           0 |  NULL |  NULL |    NULL |      NULL |         |   1.28 |     1.25 | 
|  2 |         1 |           0 | NULL |  NULL |    NULL |      NULL |         5 |           1 |  1.21 |  1.07 |   0.135 |     0.135 |         |   NULL |     NULL | 
|  3 |         2 |           1 | 1.19 |  0.97 |     0.1 |       0.1 |         2 |           0 |  NULL |  NULL |    NULL |      NULL |         |   1.19 |     0.97 | 
|  4 |         2 |           0 | NULL |  NULL |    NULL |      NULL |         5 |           0 |  NULL |  NULL |    NULL |      NULL |         |   NULL |     NULL | 
|  5 |         2 |           0 | NULL |  NULL |    NULL |      NULL |         7 |           1 |     1 |     1 |    0.15 |     0.125 |         |   NULL |     NULL | 
|  6 |         3 |           1 | 0.96 |  0.85 |     0.1 |       0.1 |         3 |           0 |  NULL |  NULL |    NULL |      NULL |         |   0.96 |     0.85 | 
|  7 |         3 |           0 | NULL |  NULL |    NULL |      NULL |         7 |           0 |  NULL |  NULL |    NULL |      NULL |         |   NULL |     NULL | 
|  8 |         4 |           1 | 0.96 |  1.15 |     0.1 |       0.1 |         4 |           0 |  NULL |  NULL |    NULL |      NULL |         |   0.96 |     1.15 | 
|  9 |         4 |           0 | NULL |  NULL |    NULL |      NULL |         6 |           1 | 0.865 |   1.1 |   0.135 |     0.135 |         |   NULL |     NULL | 
| 10 |         4 |           0 | NULL |  NULL |    NULL |      NULL |         7 |           0 |  NULL |  NULL |    NULL |      NULL |         |   NULL |     NULL | 
+----+-----------+-------------+------+-------+---------+-----------+-----------+-------------+-------+-------+---------+-----------+---------+--------+----------+
10 rows in set (0.00 sec)

