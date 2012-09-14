project (TRAP)
cmake_minimum_required (VERSION 2.8)

include(FindPythonInterp)

# determine python version string - this is missing in old Cmake versions
include(${PROJECT_SOURCE_DIR}/cmake/FindPythonVersion.cmake)

set(PYTHON_PACKAGES_DIR
    ${CMAKE_INSTALL_PREFIX}/lib/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages
    CACHE PATH "location of where you want your python modules installed"
)

install (CODE
    "execute_process(
        COMMAND ${PYTHON_EXECUTABLE} ./setup.py install
                --install-lib=${PYTHON_PACKAGES_DIR}
                --install-scripts=${CMAKE_INSTALL_PREFIX}/bin
                --install-data=${PYTHON_PACKAGES_DIR}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )"
)

