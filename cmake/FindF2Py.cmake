# +-----------------------------------------------------------------------------+
# | $Id::                                                                     $ |
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

# - Check for the presence of F2PY
#
# The following variables are set when F2PY is found:
#  F2PY_FOUND      = Set to true, if all components of F2PY have been found.
#  F2PY_EXECUTABLE = Path to the f2py executable

if (NOT F2PY_FOUND)

  ##_____________________________________________________________________________
  ## Check for the executable

  find_program (F2PY_EXECUTABLE f2py
    HINTS ${F2PY_ROOT_DIR}
    )

  ##_____________________________________________________________________________
  ## Actions taken when all components have been found

  if (F2PY_EXECUTABLE)
    set (F2PY_FOUND TRUE)
  else (F2PY_EXECUTABLE)
    set (F2PY_FOUND FALSE)
    if (NOT F2PY_FIND_QUIETLY)
      message (STATUS "Unable to find f2py executable!")
    endif (NOT F2PY_FIND_QUIETLY)
  endif (F2PY_EXECUTABLE)

  if (F2PY_FOUND)
    if (NOT F2PY_FIND_QUIETLY)
      message (STATUS "Found components for F2PY")
      message (STATUS "F2PY_EXECUTABLE = ${F2PY_EXECUTABLE}")
    endif (NOT F2PY_FIND_QUIETLY)
  else (F2PY_FOUND)
    if (F2PY_FIND_REQUIRED)
      message (FATAL_ERROR "Could not find F2PY!")
    endif (F2PY_FIND_REQUIRED)
  endif (F2PY_FOUND)

  ##_____________________________________________________________________________
  ## Mark advanced variables

  mark_as_advanced (
    F2PY_ROOT_DIR
    F2PY_EXECUTABLE
    )

endif (NOT F2PY_FOUND)
