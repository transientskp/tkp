#!/usr/bin/env bash

./setup.db.batch localhost 50000 simrsm10 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm10 ch2

python ../scripts/simrsm/insert.assoc.py 10 10

