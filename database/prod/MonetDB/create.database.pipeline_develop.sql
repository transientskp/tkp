CREATE USER "lofar" WITH PASSWORD 'cs1' NAME 'lofar database' SCHEMA "sys";
CREATE SCHEMA "pipeline_develop" AUTHORIZATION "lofar";
ALTER USER "lofar" SET SCHEMA "pipeline_develop";
