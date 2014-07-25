project (TKP)
cmake_minimum_required (VERSION 2.8)

# These are the versions of Python we support.
set(Python_ADDITIONAL_VERSIONS 2.7)

include (FindPythonInterp)
include (FindPythonLibs)
include (${PROJECT_SOURCE_DIR}/cmake/SetPythonPackagesDir.cmake)
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
