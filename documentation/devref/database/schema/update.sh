#!/bin/bash -e
$(dirname ${0})/manage.py inspectdb > $(dirname ${0})/app/models.py
$(dirname ${0})/manage.py graph_models app -a -o schema.png
