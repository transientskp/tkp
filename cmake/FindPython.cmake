# +-----------------------------------------------------------------------------+
# |   Copyright (C) 2007                                                        |
# |   Lars B"ahren (bahren@astron.nl)                                           |
# |                                                                             |
# |   This program is free software; you can redistribute it and/or modify      |
# |   it under the terms of the GNU General Public License as published by      |
# |   the Free Software Foundation; either version 2 of the License, or         |
# |   (at your option) any later version.                                       |
# |                                                                             |
# |   This program is distributed in the hope that it will be useful,           |
# |   but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# |   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             |
# |   GNU General Public License for more details.                              |
# |                                                                             |
# |   You should have received a copy of the GNU General Public License         |
# |   along with this program; if not, write to the                             |
# |   Free Software Foundation, Inc.,                                           |
# |   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                 |
# +-----------------------------------------------------------------------------+

# - Check for the presence of PYTHON
#
# The following variables are set when PYTHON is found:
#  PYTHON_FOUND      = Set to true, if all components of PYTHON have been found.
#  PYTHON_INCLUDES   = Include path for the header files of PYTHON
#  PYTHON_LIBRARIES  = Link these to use PYTHON
#  PYTHON_LFLAGS     = Linker flags (optional)

if (NOT PYTHON_FOUND)

  ## Initialize variables

  set (PYTHON_VERSION_MAJOR     0  )
  set (PYTHON_VERSION_MINOR     0  )
  set (PYTHON_VERSION_MICRO     0  )
  set (PYTHON_API_VERSION       0  )

  if (NOT PYTHON_ROOT_DIR)
    set (PYTHON_ROOT_DIR ${CMAKE_INSTALL_PREFIX})
  endif (NOT PYTHON_ROOT_DIR)

  foreach (_pythonRelease 2.7 2.6 2.5 2.4)

    find_program (PYTHON_EXECUTABLE python python${_pythonRelease}
      HINTS ${PYTHON_ROOT_DIR}
      PATHS
      /Library/Frameworks/Python.framework/Versions/${_pythonRelease}
      /sw/Library/Frameworks/Python.framework/Versions/${_pythonRelease}
      /opt/local/Library/Frameworks/Python.framework/Versions/${_pythonRelease}
      /sw
      /usr
      /usr/local
      /opt/local
      PATH_SUFFIXES bin
      NO_DEFAULT_PATH
      )

  endforeach (_pythonRelease 2.7 2.6 2.5 2.4)

  if (PYTHON_EXECUTABLE)
    execute_process(
      COMMAND ${PYTHON_EXECUTABLE} -c import\ distutils.sysconfig\;\ print\ distutils.sysconfig.get_config_vars\(\)['prefix']
      RESULT_VARIABLE PYTHON_PREFIX_ERROR
      OUTPUT_VARIABLE PYTHON_PREFIX
      OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    execute_process(
      COMMAND ${PYTHON_EXECUTABLE} -c import\ distutils.sysconfig\;\ print\ distutils.sysconfig.get_python_version\(\)
      RESULT_VARIABLE PYTHON_VER_ERROR
      OUTPUT_VARIABLE PYTHON_VERSION
      OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    execute_process(
      COMMAND ${PYTHON_EXECUTABLE} -c import\ distutils.sysconfig\;\ print\ distutils.sysconfig.get_python_inc\(\)
      RESULT_VARIABLE PYTHON_INC_ERROR
      OUTPUT_VARIABLE PYTHON_INCLUDES
      OUTPUT_STRIP_TRAILING_WHITESPACE
    )
  endif (PYTHON_EXECUTABLE)

  if (APPLE)
    # When Python <= 2.6 is installed as a framework, then libpython isn't
    # conveniently located in the directory given by Python as a prefix.
    # Instead, try and guess the prefix based on the location of the
    # executable.
    get_filename_component (APPLE_PYTHON_PREFIX ${PYTHON_EXECUTABLE} PATH)
    string (REPLACE "bin" "" APPLE_PYTHON_PREFIX ${APPLE_PYTHON_PREFIX})
    set (PYTHON_PREFIX ${PYTHON_PREFIX} ${APPLE_PYTHON_PREFIX})
  endif (APPLE)

  if (PYTHON_PREFIX)
    find_library (PYTHON_LIBRARIES python${PYTHON_VERSION} python
      PATHS ${PYTHON_PREFIX}
      PATH_SUFFIXES lib
      NO_DEFAULT_PATH
      )
  endif (PYTHON_PREFIX)

  ##_____________________________________________________________________________
  ## Test Python library for:
  ##  - library version <major.minor.release>

  if (PYTHON_INCLUDES AND PYTHON_LIBRARIES)
    ## Locate test program
    find_file (HAVE_TestPythonLibrary TestPythonLibrary.cc
      PATHS ${PROJECT_SOURCE_DIR}
      PATH_SUFFIXES cmake Modules
      )
    ## Build and run test program
    if (HAVE_TestPythonLibrary)
      try_run(PYTHON_VERSION_RUN_RESULT PYTHON_VERSION_COMPILE_RESULT
	${PROJECT_BINARY_DIR}
	${HAVE_TestPythonLibrary}
	CMAKE_FLAGS -DLINK_LIBRARIES:STRING=${PYTHON_LIBRARIES}
	COMPILE_DEFINITIONS -I${PYTHON_INCLUDES}
	RUN_OUTPUT_VARIABLE PYTHON_VERSION_OUTPUT
	)
    endif (HAVE_TestPythonLibrary)
  endif (PYTHON_INCLUDES AND PYTHON_LIBRARIES)

  ## Comile of test program successful?
  if (PYTHON_VERSION_COMPILE_RESULT)
    ## Run of test program successful?
    if (PYTHON_VERSION_RUN_RESULT)

      ## Library version _________________________

      string(REGEX REPLACE "PY_MAJOR_VERSION ([0-9]+).*" "\\1" PYTHON_VERSION_MAJOR ${PYTHON_VERSION_OUTPUT})
      string(REGEX REPLACE ".*PY_MINOR_VERSION ([0-9]+).*" "\\1" PYTHON_VERSION_MINOR ${PYTHON_VERSION_OUTPUT})
      string(REGEX REPLACE ".*PY_MICRO_VERSION ([0-9]+).*" "\\1" PYTHON_VERSION_MICRO ${PYTHON_VERSION_OUTPUT})
      string(REGEX REPLACE ".*PYTHON_API_VERSION ([0-9]+).*" "\\1" PYTHON_API_VERSION ${PYTHON_VERSION_OUTPUT})

    else (PYTHON_VERSION_RUN_RESULT)
      message (STATUS "[Python] Failed to run TestPythonLibrary!")
    endif (PYTHON_VERSION_RUN_RESULT)
  else (PYTHON_VERSION_COMPILE_RESULT)
    message (STATUS "[Python] Failed to compile TestPythonLibrary!")
  endif (PYTHON_VERSION_COMPILE_RESULT)

  ## Assemble full version of library
  set (PYTHON_VERSION "${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}.${PYTHON_VERSION_MICRO}")

  ##_____________________________________________________________________________
  ## Actions taken when all components have been found

  if (PYTHON_INCLUDES AND PYTHON_LIBRARIES)
    set (PYTHON_FOUND TRUE)
  else (PYTHON_INCLUDES AND PYTHON_LIBRARIES)
    set (PYTHON_FOUND FALSE)
    if (NOT PYTHON_FIND_QUIETLY)
      if (NOT PYTHON_INCLUDES)
	message (STATUS "Unable to find PYTHON header files!")
      endif (NOT PYTHON_INCLUDES)
      if (NOT PYTHON_LIBRARIES)
	message (STATUS "Unable to find PYTHON library files!")
      endif (NOT PYTHON_LIBRARIES)
    endif (NOT PYTHON_FIND_QUIETLY)
  endif (PYTHON_INCLUDES AND PYTHON_LIBRARIES)

  if (PYTHON_FOUND)
    if (NOT PYTHON_FIND_QUIETLY)
      message (STATUS "[FindPython] Found components for Python.")
      message (STATUS "PYTHON_VERSION   = ${PYTHON_VERSION}"   )
      message (STATUS "PYTHON_INCLUDES  = ${PYTHON_INCLUDES}"  )
      message (STATUS "PYTHON_LIBRARIES = ${PYTHON_LIBRARIES}" )
    endif (NOT PYTHON_FIND_QUIETLY)
  else (PYTHON_FOUND)
    if (PYTHON_FIND_REQUIRED)
      message (FATAL_ERROR "[FindPython] Could not find Python!")
    endif (PYTHON_FIND_REQUIRED)
  endif (PYTHON_FOUND)

  set (PYTHON_LOCAL_PACKAGE_DIR "lib/python")

  ##_____________________________________________________________________________
  ## Mark advanced variables

  mark_as_advanced (
    PYTHON_VERSION
    PYTHON_VERSION_MAJOR
    PYTHON_VERSION_MINOR
    PYTHON_INCLUDES
    PYTHON_LIBRARIES
    PYTHON_LOCAL_PACKAGE_DIR
    )

endif (NOT PYTHON_FOUND)
