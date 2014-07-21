Vagrant
=======

To install TRAP you can also use Vagrant. Vagrant is a thin shell around
virtual machine technology.


Terminology
-----------

 * Host - the machine where you install Vagrant on
 * Guest - the virtual machine created by vagrant.


Installation
------------

Download `Virtualbox <https://www.virtualbox.org/>`_ and
`Vagrant <http://www.vagrantup.com/>`_ and install them. On Ubuntu 14.04 you
can simply do::

    $ sudo apt-get install virtualbox vagrant


Usage
-----

Inside the TRAP source tree root run the command::

    $ vagrant up

This will set up a virtualmachine with all dependencies installed, TRAP installed
Banana configured & installed and a webserver serving banana on
http://localhost:8086 .

You can enter the guest by running::

    $ vagrant ssh


The TRAP source code on the host is mounted inside the guest as `/vagrant`. All
files put inside this folder on the host will appear on the guest, and visa
versa. The vagrant provision script created a TRAP project and job config for
you in `/vagrant/vagrantproject`. This project takes all data files in
`/vagrant/vagrant/data`.


Running the pipeline
--------------------

you can modify the configuration to your needs. The easiest way to get started
is to copy your data files into `/vagrant/vagrant/data` and inside
`/vagrant/vagrantproject` run::

    $ ./manage.py run vagrantjob

