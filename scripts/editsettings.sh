#!/bin/bash
file="/home/scheers/tkp-code/pipe/python-packages/tkp_lib/edset.py"
if [ -e $file ]; then
	echo "File exists"
	sed 's/database_enabled = False/database_enabled = True/g' /home/scheers/tkp-code/pipe/python-packages/tkp_lib/edset.py > /home/scheers/tkp-code/pipe/python-packages/tkp_lib/edset.py.new
	cp /home/scheers/tkp-code/pipe/python-packages/tkp_lib/edset.py.new /home/scheers/tkp-code/pipe/python-packages/tkp_lib/edset.py
else
	echo "File exists"
fi
