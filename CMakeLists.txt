project (TRAP)
cmake_minimum_required (VERSION 2.6)
cmake_policy (VERSION 2.6)

include(FindPythonInterp)
set(PYTHON_PACKAGES_DIR lib/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages)

install (CODE
    "execute_process(
        COMMAND ${PYTHON_EXECUTABLE} ./setup.py install
        --install-lib=${CMAKE_INSTALL_PREFIX}/${PYTHON_PACKAGES_DIR}
        --install-scripts=${CMAKE_INSTALL_PREFIX}/bin
        --install-data=${CMAKE_INSTALL_PREFIX}/${PYTHON_PACKAGES_DIR}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})"
)


