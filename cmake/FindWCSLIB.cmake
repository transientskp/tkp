# +-----------------------------------------------------------------------------+
# | $Id::                                                                     $ |
# +-----------------------------------------------------------------------------+
# |   Copyright (C) 2007, 2011                                                  |
# |   Lars B"ahren, Evert Rol                                                   |
# |   LOFAR TKP Discovery WG (discovery@transientskp.org)                       |
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

# - Check for the presence of WCSLIB
#
# The following variables are set when WCSLIB is found:
#  WCSLIB_FOUND      = Set to true, if all components of WCSLIB have been found.
#  WCSLIB_INCLUDES   = Include path for the header files of WCSLIB
#  WCSLIB_LIBRARIES  = Link these to use WCSLIB
#  WCSLIB_LFLAGS     = Linker flags (optional)

if (NOT WCSLIB_FOUND)

  ## Initialize variables

  if (NOT WCSLIB_ROOT_DIR)
    set (WCSLIB_ROOT_DIR ${CMAKE_INSTALL_PREFIX})
  endif (NOT WCSLIB_ROOT_DIR)

  ##_____________________________________________________________________________
  ## Check for the header files

  find_path (WCSLIB_INCLUDES wcs.h wcshdr.h
    PATHS ${WCSLIB_ROOT_DIR} /sw /sw/wcslib /usr /usr/local/wcslib /usr/local/include/wcslib /opt/local/wcslib /opt/wcslib/include/wcslib /opt/local/include/wcslib /opt/cep/wcslib/include/wcslib
    PATH_SUFFIXES include include/wcslib
    )
  message (STATUS "WCSLIB_INCLUDES = " ${WCSLIB_INCLUDES})

  ##_____________________________________________________________________________
  ## Check for the library

  find_library (WCSLIB_LIBRARIES wcs
    PATHS ${WCSLIB_ROOT_DIR} /sw /usr /usr/local /opt/local /opt/wcslib /opt/cep/wcslib
    PATH_SUFFIXES lib
    )
  message (STATUS "WCSLIB_LIBRARIES = " ${WCSLIB_LIBRARIES})

  if (WCSLIB_INCLUDES AND WCSLIB_LIBRARIES)
    set (WCSLIB_FOUND TRUE)
  else (WCSLIB_INCLUDES AND WCSLIB_LIBRARIES)
    set (WCSLIB_FOUND FALSE)
    if (NOT WCSLIB_FIND_QUIETLY)
      if (NOT WCSLIB_INCLUDES)
        message (STATUS "Unable to find WCSLIB header files!")
      endif (NOT WCSLIB_INCLUDES)
      if (NOT WCSLIB_LIBRARIES)
        message (STATUS "Unable to find WCSLIB library files!")
      endif (NOT WCSLIB_LIBRARIES)
    endif (NOT WCSLIB_FIND_QUIETLY)
  endif (WCSLIB_INCLUDES AND WCSLIB_LIBRARIES)

  if (WCSLIB_FOUND)
    if (NOT WCSLIB_FIND_QUIETLY)
      message (STATUS "Found components for WCSLIB")
      message (STATUS "WCSLIB_INCLUDES  = ${WCSLIB_INCLUDES}"  )
      message (STATUS "WCSLIB_LIBRARIES = ${WCSLIB_LIBRARIES}" )
    endif (NOT WCSLIB_FIND_QUIETLY)
  else (WCSLIB_FOUND)
    if (WCSLIB_FIND_REQUIRED)
      message (FATAL_ERROR "Could not find WCSLIB!")
    endif (WCSLIB_FIND_REQUIRED)
  endif (WCSLIB_FOUND)

  ##_____________________________________________________________________________
  ## Mark advanced variables

  mark_as_advanced (
    WCSLIB_INCLUDES
    WCSLIB_LIBRARIES
   )

endif (NOT WCSLIB_FOUND)
