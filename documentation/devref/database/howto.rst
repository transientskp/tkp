+++++
HOWTO
+++++

Create a schema diagram
=======================

As shown in the :ref:`schema documentation <database-schema>`.

Starting from a completely blank Ubuntu 12.04 system (I used Docker)::

  $ apt-get install python-django git \
    python-django-extensions python-pygraphviz

  $ git clone https://github.com/transientskp/banana.git

  $ cd banana

  $ cat > bananaproject/settings/__init__.py
  INSTALLED_APPS = ['banana', 'django_extensions']

  $ ./manage.py graph_models -o schema.png banana

Note that you don't actually need to connect to a database for this.
