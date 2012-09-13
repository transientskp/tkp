project (TRAP)
cmake_minimum_required (VERSION 2.8)

include(FindPythonInterp)

# determine python version string - this is missing in old Cmake versions
if(PYTHON_EXECUTABLE)
    execute_process(COMMAND "${PYTHON_EXECUTABLE}" --version ERROR_VARIABLE _VERSION OUTPUT_QUIET ERROR_STRIP_TRAILING_WHITESPACE)
    string(REPLACE "Python " "" PYTHON_VERSION_STRING "${_VERSION}")
    string(REGEX REPLACE "^([0-9]+)\\.[0-9]+\\.[0-9]+.*" "\\1" PYTHON_VERSION_MAJOR "${PYTHON_VERSION_STRING}")
    string(REGEX REPLACE "^[0-9]+\\.([0-9])+\\.[0-9]+.*" "\\1" PYTHON_VERSION_MINOR "${PYTHON_VERSION_STRING}")
    string(REGEX REPLACE "^[0-9]+\\.[0-9]+\\.([0-9]+).*" "\\1" PYTHON_VERSION_PATCH "${PYTHON_VERSION_STRING}")
endif()

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

