if (NOT DEFINED PYTHON_PACKAGES_DIR)
    # check if we are inside a virtualenv
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} -c "import sys; print hasattr(sys, 'real_prefix')"
        OUTPUT_VARIABLE INSIDE_VIRTUALENV
        )
    STRING(REGEX REPLACE "(\r?\n)+$" "" INSIDE_VIRTUALENV "${INSIDE_VIRTUALENV}")
    message (STATUS "INSIDE_VIRTUALENV = " ${INSIDE_VIRTUALENV})

    IF (${INSIDE_VIRTUALENV} MATCHES "True")
        execute_process(
            COMMAND ${PYTHON_EXECUTABLE} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"
            OUTPUT_VARIABLE PYTHON_PACKAGES_DIR
            )
    else()
        execute_process(
            COMMAND ${PYTHON_EXECUTABLE} -c "import site; print site.getsitepackages()[0]"
            OUTPUT_VARIABLE PYTHON_PACKAGES_DIR
            )
    endif()
endif()

STRING(REGEX REPLACE "(\r?\n)+$" "" PYTHON_PACKAGES_DIR "${PYTHON_PACKAGES_DIR}")
set (PYTHON_PACKAGES_DIR ${PYTHON_PACKAGES_DIR} CACHE PATH "Python package installation directory")
MARK_AS_ADVANCED(PYTHON_PACKAGES_DIR)

message (STATUS "PYTHON_PACKAGES_DIR = " ${PYTHON_PACKAGES_DIR})
