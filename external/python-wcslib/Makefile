# Detect operating system
OS = $(shell uname -s)

# Suggested paths for Mac OS
#CC = /opt/local/bin/c++
#PYTHON_INCLUDE = -I/opt/local/include/python2.5
#BOOST_INCLUDE  = -I/opt/local/include
#WCSLIB_INCLUDE = -I/Users/jds/apps/include/wcslib

#BOOST_LIB  = /opt/local/lib/libboost_python-mt.a
#WCSLIB_LIB = -L/Users/jds/apps/lib

# Suggested paths for Linux
CC = /usr/bin/c++
PYTHON_INCLUDE = -I/usr/include/python2.6
BOOST_INCLUDE  = -I/usr/include/boost
WCSLIB_INCLUDE = -I/usr/local/include/wcslib

BOOST_LIB  = -L/usr/lib
WCSLIB_LIB = -L/usr/local/lib

default: wcslib.cpp
ifeq (${OS},Darwin)
	${CC} -fPIC ${PYTHON_INCLUDE} ${BOOST_INCLUDE} ${WCSLIB_INCLUDE} -bundle -headerpad_max_install_names -undefined dynamic_lookup -o wcslib.so ${WCSLIB_LIB} -lwcs.4.3 ${BOOST_LIB} wcslib.cpp
else
	${CC} -fPIC ${PYTHON_INCLUDE} ${BOOST_INCLUDE} ${WCSLIB_INCLUDE} -shared -Wl,-soname,wcslib.so -o wcslib.so ${BOOST_LIB} ${WCSLIB_LIB} -lboost_python -lwcs wcslib.cpp
endif
