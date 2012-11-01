
Setting up the TKP database
===========================

Before running download the skymodel files from somewhere and
make symlinks, something like this::

 $ ln -s /scratch/catfiles/NVSS-all_strip.csv catfiles/nvss/nvss.csv
 $ ln -s /scratch/catfiles/VLSS-all_strip.csv catfiles/vlss/vlss.csv
 $ ln -s /scratch/catfiles/WENSS-all_strip.csv catfiles/wenss/wenss.csv

Note that the database user needs to be able to access these files,
not your current id.

then run the setup script to populate your database::
 
  $ ./setup.sh


Upgrading your database
=======================

If you already have a database and want to upgrade to a later version
run the upgrade script::

  $ ./upgrade.py -h


Creating an upgrade script
==========================

 1. create an upgrade sql file (2_to_3.sql for example) and put the
    sql statements in it required to upgrade to this version
 2. also create an downgrade sql (3_to_2.sql) file that inverses the
    changes described in point 1.
 3. update the current version in sql/tables/version.sql.

