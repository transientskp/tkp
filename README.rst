NB THIS REPOSITORY HAS BEEN DEPRECATED.

Latest database files are now kept in the tkp repository, in the 
database folder.

This repository is currently being kept for reference but 
will be deleted eventually.


Setting up the TKP database
===========================

Before running download the skymodel files from somewhere and
make symlinks, something like this::

 $ ln -s /scratch/catfiles/NVSS-all_strip.csv catfiles/nvss/nvss.csv
 $ ln -s /scratch/catfiles/VLSS-all_strip.csv catfiles/vlss/vlss.csv
 $ ln -s /scratch/catfiles/WENSS-all_strip.csv catfiles/wenss/wenss.csv

then run the setup script to populate your database::
 
  $ ./setup.sh

