## Name of the project handled by CMake
project (TKP)

## Minimum required version of CMake to configure the project
cmake_minimum_required (VERSION 2.6)

## Enforced CMake policy 
cmake_policy (VERSION 2.6)


##  find the stuf we need
## ==============================================================================

foreach (_syslib dl m pthread util z)

  string (TOUPPER ${_syslib} _syslibVar)

  find_library (${_syslibVar}_LIBRARY
    NAMES ${_syslib}
    PATHS ${DAL_FIND_PATHS}
    PATH_SUFFIXES lib
    )

endforeach (_syslib)

include (${PROJECT_SOURCE_DIR}/cmake/FindBoost_TKP.cmake)
include (${PROJECT_SOURCE_DIR}/cmake/FindF2Py.cmake)
include (${PROJECT_SOURCE_DIR}/cmake/FindCFITSIO.cmake)
include(FindPythonInterp)
include(FindPythonLibs)
set(PYTHON_LOCAL_PACKAGE_DIR lib/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR})
include (${PROJECT_SOURCE_DIR}/cmake/FindWCSLIB.cmake)

##  Configuration summary
## ==============================================================================

message (STATUS "+------------------------------------------------------------+")

message (STATUS "CMAKE_SYSTEM               = ${CMAKE_SYSTEM}"           )
message (STATUS "CMAKE_SYSTEM_NAME          = ${CMAKE_SYSTEM_NAME}"      )
message (STATUS "CMAKE_SYSTEM_PROCESSOR     = ${CMAKE_SYSTEM_PROCESSOR}" )
message (STATUS "CMAKE_SYSTEM_VERSION       = ${CMAKE_SYSTEM_VERSION}"   )
message (STATUS "Found Boost++ installation = ${BOOST_FOUND}"            )
message (STATUS "  .. BOOST_ROOT_DIR        = ${BOOST_ROOT_DIR}"         )
message (STATUS "  .. BOOST_VERSION         = ${BOOST_VERSION}"          )
message (STATUS "  .. BOOST_INCLUDES        = ${BOOST_INCLUDES}"         )
message (STATUS "  .. BOOST_LIBRARIES       = ${BOOST_LIBRARIES}"        )
message (STATUS "Fount Python installation  = ${PYTHON_FOUND}"           )
message (STATUS "  .. Python version        = ${PYTHON_VERSION}"         )
message (STATUS "  .. Include directory     = ${PYTHON_INCLUDES}"        )
message (STATUS "Found CFITSIO installation = ${CFITSIO_FOUND}"          )
message (STATUS "Found WCSLIB installation  = ${WCSLIB_FOUND}"           )
message (STATUS "Found f2py compiler        = ${F2PY_FOUND}"             )

message (STATUS "+------------------------------------------------------------+")

add_subdirectory (external)
add_subdirectory (enduser_scripts)

add_custom_target (tkp_python_lib
  ALL
  COMMAND ${PYTHON_EXECUTABLE} ./setup.py build
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  COMMENT "Compiling Python TKP package ..."
  )

install (CODE
	"execute_process(
	    COMMAND ${PYTHON_EXECUTABLE} ./setup.py install --install-lib=${CMAKE_INSTALL_PREFIX}/${PYTHON_LOCAL_PACKAGE_DIR}
	    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
	    )"
	)
