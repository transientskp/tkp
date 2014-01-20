#!/bin/sh

## install all requirements
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:gijzelaar/aartfaac
sudo apt-get update
sudo apt-get install -y libcasacore-dev casacore-data pyrap python-scipy \
    python-pygresql build-essential python-pip python-numpy postgresql cmake \
    libboost-python-dev wcslib-dev gfortran python-psycopg2 python-pyfits git

## compile and install trap
mkdir -p /vagrant/build
cd /vagrant/build
cmake ..
make clean
make
sudo make install
cd ..
pip install -r requirements.txt

## create trap project
cd /vagrant
tkp-manage.py initproject vagrantproject || true
cd vagrantproject
./manage.py initjob vagrantjob || true


## setup & configure banana
cd /opt
git clone https://github.com/transientskp/banana || true
cd banana
cp bananaproject/settings/local_example.py bananaproject/settings/local.py
pip install -r requirements.txt