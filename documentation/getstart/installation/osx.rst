.. _osx:

===
OSX
===

********
Preamble
********

Although there are many ways to install TKP and it dependecies, we find that
using the `Homebrew`_ gives a smooth installation experience.


************
Installation
************

* Install homebrew::

    $ ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"
    $ brew doctor

* Now install the `Homebrew SKA tap`_, which contains all kind of radio
  astronomy software::

    $ brew tap ska-sa/tap

* Install all the TKP library dependencies::

    $ brew install gfortran python pyrap

* Now from the TKP source root directory install all Python dependencies with::

    $ pip install -r requirements.txt


Optional dependencies
=====================

Database
--------
If you want to run the pipeline you need to store the results somewhere. TKP
currently supports two database systems, `PostgreSQL`_ and `MonetDB`_. Pick one.

PostgreSQL
^^^^^^^^^^
You can easily install PostgreSQL using these commands::

    $ brew install postgresql

Now you need to initialize the database::

    $ initdb /usr/local/var/postgres -E utf8

Finally start the database server::

    $ pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start

If you need to know more the ``postgresql`` "brew" is a good place to start::

    $ brew info postgresql


MonetDB
^^^^^^^

You can install MonetDB using these commands::

    $ brew install monetdb

Now you need to initialize the database somewhere::

    $ mkdir ~/Var $$ ~/Var  # Or whatever you prefer
    $ monetdbd create monetdb
    $ monetdbd start monetdb


Broker
------

If you want to run `Celery <celery-intro>` workers, you need a broker.  We
suggest `RabbitMQ`_::

    $ brew install rabbitmq

To run a rabbitmq server run::

    $ rabbitmq-server

MongoDB
-------

If you want to use the :ref:`pixel store <mongodb-intro>`, you will need to
installed MongoDB on the chosen database host::

    $ brew install mongodb

See the `MongoDB documentation
<http://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x>`_ for
full instructions.

You will also need to make sure the Python wrapper is available on your client
machine::

    $ pip install python-pymongo


.. _RabbitMQ: http://www.rabbitmq.com/
.. _homebrew: http://mxcl.github.io/homebrew/
.. _homebrew SKA tap: https://github.com/ska-sa/homebrew-tap/
.. _PostgreSQL: http://www.postgresql.org/
.. _MonetDB: http://www.monetdb.org/
