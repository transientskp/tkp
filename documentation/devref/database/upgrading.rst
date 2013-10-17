.. _database_upgrading:

+++++++++
Upgrading
+++++++++

The TKP database repo has basic support for upgrading an existing database schema to a newer version. Note that the
migration SQL scripts still need to be written by hand, currently the upgrade script only determines which upgrade
scripts should be ran.

Usage
=====

There is an script with the name **upgrade** in the TKP database repo. Run this script with **-h** to see all
options. The script will check which version the database is running by checking the **version table** in the
TKP database on a given host.


Adding new upgrade scripts
==========================

The idea is that for every change to the database one should increment the **revision** defined in
**database/sql/tables/version.sql**. Next a new script should be created in **database/sql/upgrade** which
would migrate an existing TKP database instance to the latest revision.  A downgrade script should also be provided
which would undo a upgrade in case something goes wrong.

Naming convention
=================

The scripts in **database/sql/upgrade** should be named <old>_to_<new>.sql, for example the script 1_to_2.sql
contains the SQL statements to migrate a database with revision **1** to a database with revision **2**.
