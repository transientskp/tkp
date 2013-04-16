How to create the schema as shown in tkp-doc
============================================

get python-monetdb::

  $ pip install python-monetdb

get djonet, the MonetDB Django backend::

  $ pip install djonet

get the django extensions::

  $ pip install django-extensions

get banana::

  https://github.com/gijzelaerr/banana

Edit the banana/settings.py and set the tkpdb database
parameters to represent your system setup.

To reverse engineer the Django models van the MonetDB schema::

  $ ./manage.py inspectdb --database=tkpdb

To create a graphical representation of the Django models::

  $ ./manage.py graph_models -o schema.png tkpdb


