#! /bin/bash

#
# This scripts needs to be run before using the load.cat.*.sql scripts
# It will update the locations of various catalogs inside the sql scripts
# with the correct file on the current system (or at least attempts to do so).
#
# This scripts is automatically run by the default setup.db.batch script, so
# if that script is used to initialize a database, this needs does not need to 
# be run (but it would do no harm if run anyway).
#
# 2011-03-24
# At the moment, only three files will be properly adjusted:
#     load.cat.wenss.sql
#     load.cat.nvss.sql
#     load.cat.vlss.sql
# These are also the only three catalogs currently loaded through the 
# main setup.db.batch scripts
# Note that this script may be run either directly from the load/ subdir,
# or from the batches/ subdir; hence the relative path names in the sed commands


# I'm lazy, so we simply to the same thing three times
# Of course, maintenance wise, duplicate code is not a good thing,
# so at some point this should be turned into a loop or function

# one: WENSS

pwd
wenss_catfile=""
dir=`dirname $0`
wenss_files=`grep -i 'WENSS-all_strip.csv' $dir/load.cat.wenss.sql`
IFS="
"
for filename in $wenss_files
do
#  echo "$filename"
  catfile=${filename#"/* '"}
  catfile=${catfile%"' */"}
  if [[ -e "$catfile" && -f "$catfile" && -s "$catfile" ]]
  then
      wenss_catfile=$catfile
      break
  fi
done
if [[ -z "$wenss_catfile" ]]
then
  echo "Error: can't find WENSS catalog file"
  exit 1;
fi
echo "WENSS local catalogus file: $wenss_catfile"
sed -i.bck "s#/\* '${wenss_catfile}' \*/#'${wenss_catfile}'#" ${dir}/../load/load.cat.wenss.sql



# two: NVSS
nvss_catfile=""
dir=`dirname $0`
nvss_files=`grep -i 'NVSS-all_strip.csv' $dir/load.cat.nvss.sql`
IFS="
"
for filename in $nvss_files
do
#  echo "$filename"
  catfile=${filename#"/* '"}
  catfile=${catfile%"' */"}
  if [[ -e "$catfile" && -f "$catfile" && -s "$catfile" ]]
  then
      nvss_catfile=$catfile
      break
  fi
done
if [[ -z "$nvss_catfile" ]]
then
  echo "Error: can't find NVSS catalog file"
  exit 1;
fi
echo "NVSS local catalogus file: $nvss_catfile"
sed -i.bck "s#/\* '${nvss_catfile}' \*/#'${nvss_catfile}'#" ${dir}/../load/load.cat.nvss.sql


# three: VLSS
vlss_catfile=""
dir=`dirname $0`
vlss_files=`grep -i 'VLSS-all_strip.csv' $dir/load.cat.vlss.sql`
IFS="
"
for filename in $vlss_files
do
#  echo "$filename"
  catfile=${filename#"/* '"}
  catfile=${catfile%"' */"}
  if [[ -e "$catfile" && -f "$catfile" && -s "$catfile" ]]
  then
      vlss_catfile=$catfile
      break
  fi
done
if [[ -z "$vlss_catfile" ]]
then
  echo "Error: can't find VLSS catalog file"
  exit 1;
fi
echo "VLSS local catalogus file: $vlss_catfile"
sed -i.bck "s#/\* '${vlss_catfile}' \*/#'${vlss_catfile}'#" ${dir}/../load/load.cat.vlss.sql
