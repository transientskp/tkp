project (TKP)
cmake_minimum_required (VERSION 2.8)

foreach (_syslib dl m pthread util z)
    string (TOUPPER ${_syslib} _syslibVar)
    find_library (${_syslibVar}_LIBRARY
        NAMES ${_syslib}
        PATHS ${DAL_FIND_PATHS}
        PATH_SUFFIXES lib
    )
endforeach (_syslib)

find_package(Boost)
include (${PROJECT_SOURCE_DIR}/cmake/FindF2Py.cmake)
include (${PROJECT_SOURCE_DIR}/cmake/FindCFITSIO.cmake)
include (FindPythonInterp)
include (FindPythonLibs)
include(${PROJECT_SOURCE_DIR}/cmake/FindPythonVersion.cmake)


set(PYTHON_PACKAGES_DIR
    ${CMAKE_INSTALL_PREFIX}/lib/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages
    CACHE PATH "location of where you want your python modules installed"
)

# this is included later since it needs PYTHON_PACKAGES_DIR
include (${PROJECT_SOURCE_DIR}/cmake/FindWCSLIB.cmake)

add_subdirectory (external)
add_subdirectory (enduser_scripts)

install (CODE
    "execute_process(
        COMMAND ${PYTHON_EXECUTABLE} ./setup.py install
                --install-lib=${PYTHON_PACKAGES_DIR}
                --install-scripts=${CMAKE_INSTALL_PREFIX}/bin
                --install-data=${PYTHON_PACKAGES_DIR}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )"
)
