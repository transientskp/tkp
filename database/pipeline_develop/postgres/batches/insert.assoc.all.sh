#!/usr/bin/env bash

echo DB setup 10 10000
./setup.db.batch localhost 50000 simrsm10 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm10 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py ldb001 10 10000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm10
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm10
echo Done

echo DB setup 20 1000
./setup.db.batch localhost 50000 simrsm20 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm20 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 20 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm20
$sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm20
echo Done

echo DB setup 50 1000
./setup.db.batch localhost 50000 simrsm50 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm50 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 50 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm50
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm50
echo Done

echo DB setup 100 1000
./setup.db.batch localhost 50000 simrsm100 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm100 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 100 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm100
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm100
echo Done

echo DB setup 200 1000
./setup.db.batch localhost 50000 simrsm200 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm200 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 200 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm200
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm200
echo Done

echo DB setup 500 1000
./setup.db.batch localhost 50000 simrsm500 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm500 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 500 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm500
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm500
echo Done

echo DB setup 1000 1000
./setup.db.batch localhost 50000 simrsm1000 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm1000 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 1000 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm1000
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm1000
echo Done

echo DB setup 2000 1000
./setup.db.batch localhost 50000 simrsm2000 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm2000 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 2000 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm2000
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm2000
echo Done

echo DB setup 5000 1000
./setup.db.batch localhost 50000 simrsm5000 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm5000 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 5000 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm5000
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm5000
echo Done

echo DB setup 10000 1000
./setup.db.batch localhost 50000 simrsm10000 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm10000 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 10000 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm10000
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm10000
echo Done

echo DB setup 20000 1000
./setup.db.batch localhost 50000 simrsm20000 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm20000 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 20000 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm20000
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm20000
echo Done

echo DB setup 50000 1000
./setup.db.batch localhost 50000 simrsm50000 50001 tjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 simrsm50000 ch2
echo Python script
python ../scripts/simrsm/insert.assoc.py 50000 1000
echo destroy db again
sudo monetdb -hlocalhost -p50001 -Ptjbai1ZkXFvBiquhYEITcK0IcJVaTq7cx7 stop simrsm50000
sudo monetdb -h$1 -p$4 -P$5 destroy -f simrsm50000
echo Done

