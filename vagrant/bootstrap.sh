#!/bin/bash -ev

cp /vagrant/vagrant/apt.sources.list /etc/apt/sources.list

## install all requirements
apt-get install -y software-properties-common
add-apt-repository ppa:ska-sa/main
apt-get update
cat /vagrant/vagrant/debian_packages | xargs apt-get install -y -q

## compile and install trap
mkdir -p /vagrant/build
cd /vagrant/build
rm -rf *
cmake .. -DINSTALL_TKP=OFF
make clean
make
make install
cd ..
pip install -r requirements.txt

## create trap project
export PYTHONPATH=/vagrant
cd /vagrant
/vagrant/tkp/bin/tkp-manage.py initproject vagrantproject || true
cd vagrantproject
./manage.py initjob vagrantjob || true
cp /vagrant/vagrant/pipeline.cfg pipeline.cfg
cp /vagrant/vagrant/images_to_process.py vagrantjob/images_to_process.py


## setup & configure banana
cd /opt
git clone https://github.com/transientskp/banana || true
cd banana
pip install -r requirements.txt
cp /vagrant/vagrant/apache.conf /etc/apache2/sites-enabled/000-default.conf 
cp /vagrant/vagrant/banana_settings.py /opt/banana/bananaproject/settings/local.py
cd /opt/banana
./manage.py collectstatic --noinput
service apache2 restart

## setup a database for TRAP
echo "CREATE USER vagrant WITH PASSWORD 'vagrant' CREATEDB;" | sudo -u postgres psql || true
sudo -u vagrant createdb vagrant || true
sudo -E -u vagrant PYTHONPATH=/vagrant /vagrant/tkp/bin/tkp-manage.py  initdb -y
