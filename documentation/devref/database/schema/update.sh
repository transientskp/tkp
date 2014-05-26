#!/bin/bash -e
./manage.py inspectdb > app/models.py
./manage.py graph_models app -a -o schema.png
