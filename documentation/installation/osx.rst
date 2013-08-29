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

If you want to run `Celery`_ workers, you need a broker. There are multiple
`brokers`_ where you can choose from. If you do not have a compelling reason
to choose another, we suggest `RabbitMQ`_::

    $ brew install rabbitmq

To run a rabbitmq server run::

    $ rabbitmq-server


.. _Celery: http://www.celeryproject.org/
.. _brokers: http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html
.. _RabbitMQ: http://www.rabbitmq.com/
.. _homebrew: http://mxcl.github.io/homebrew/
.. _homebrew SKA tap: https://github.com/ska-sa/homebrew-tap/
.. _PostgreSQL: http://www.postgresql.org/
.. _MonetDB: http://www.monetdb.org/
