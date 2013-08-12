project (TKP)
cmake_minimum_required (VERSION 2.8)

set(Python_ADDITIONAL_VERSIONS 2.7 2.6)

foreach (_syslib dl m pthread util z)
    string (TOUPPER ${_syslib} _syslibVar)
    find_library (${_syslibVar}_LIBRARY
        NAMES ${_syslib}
        PATHS ${DAL_FIND_PATHS}
        PATH_SUFFIXES lib
    )
endforeach (_syslib)

include (${PROJECT_SOURCE_DIR}/cmake/FindF2Py.cmake)
include (${PROJECT_SOURCE_DIR}/cmake/FindCFITSIO.cmake)
include (FindPythonInterp)
include (FindPythonLibs)
include(${PROJECT_SOURCE_DIR}/cmake/FindPythonVersion.cmake)


# check if we are inside a virtualenv 
execute_process(
    COMMAND python -c "import sys; print hasattr(sys, 'real_prefix')"
    OUTPUT_VARIABLE INSIDE_VIRTUALENV
    )
STRING(REGEX REPLACE "(\r?\n)+$" "" INSIDE_VIRTUALENV "${INSIDE_VIRTUALENV}")
message (STATUS "INSIDE_VIRTUALENV = " ${INSIDE_VIRTUALENV})

IF (${INSIDE_VIRTUALENV} MATCHES "True")
    execute_process(
        COMMAND python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"
        OUTPUT_VARIABLE PYTHON_PACKAGES_DIR
        )
else()
    execute_process(
        COMMAND python -c "import site; print site.getsitepackages()[0]"
        OUTPUT_VARIABLE PYTHON_PACKAGES_DIR
        )
endif()

STRING(REGEX REPLACE "(\r?\n)+$" "" PYTHON_PACKAGES_DIR "${PYTHON_PACKAGES_DIR}")
message (STATUS "PYTHON_PACKAGES_DIR = " ${PYTHON_PACKAGES_DIR})


# this is included later since it needs PYTHON_PACKAGES_DIR
include (${PROJECT_SOURCE_DIR}/cmake/FindWCSLIB.cmake)

add_subdirectory (external)

set(INSTALL_TKP ON CACHE BOOL "install TKP python lib")

if(INSTALL_TKP)
    install (CODE
        "execute_process(
            COMMAND ${PYTHON_EXECUTABLE} ./setup.py install
                    --install-lib=${PYTHON_PACKAGES_DIR}
                    --install-scripts=${CMAKE_INSTALL_PREFIX}/bin
                    --install-data=${PYTHON_PACKAGES_DIR}
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        )"
    )
endif()
