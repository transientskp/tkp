#!/bin/sh
# This script creates a tar file containing the MySQL and MonetDB code
# and the catalog data files
# 

tar -cvvf dbcode.tar MySQL/ \
                     MonetDB/ \
                     -C ~/databases/ catalogs/

gzip dbcode.tar
