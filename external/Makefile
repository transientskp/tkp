INSTALL_PREFIX=/opt/tkp

# Detect operating system
OS = $(shell uname -s)

PYTHON_INCLUDE = -I$(shell python-config --prefix)
BOOST_INCLUDE  = -I/usr/include/boost
WCSLIB_INCLUDE = -I/usr/local/include/wcslib

CC = /usr/bin/gcc
CXX = /usr/bin/g++
PYTHON = /usr/bin/python
F2PY = /usr/bin/f2py

CXX_LIBS = -lwcs.4.3 -lboost_python
ifeq (${OS},Darwin)
	CC_FLAGS = -bundle -headerpad_max_install_names -undefined dynamic_lookup
	CXX_FLAGS = $(CC_FLAGS)
else
	CC_FLAGS = -shared -Wl,-soname,libwcstools.so.1
	CXX_FLAGS = -shared -Wl,-soname,wcslib.so
endif

CXX_INCLUDES = ${PYTHON_INCLUDE} ${BOOST_INCLUDE} ${WCSLIB_INCLUDE} 
BOOST_LIB  = -L/usr/lib
WCSLIB_LIB = -L/usr/local/lib




all: deconv.so libwcstools.so python_wcslib.so


deconv.so: deconv/deconv.f
	cd deconv; $(MAKE) 

libwcstools.so: 
	cd libwcstools; $(MAKE)

python_wcslib.so:
	cd python-wcslib; $(MAKE)


clean: 
	rm deconv/deconv.so libwcstools/libwccstools.so python-wcslib/wcslib.so
