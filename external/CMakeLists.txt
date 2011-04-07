
## ==============================================================================
##
##  Project subdirectories
##
## ==============================================================================

add_subdirectory (libwcstools)

if (F2PY_EXECUTABLE)
  add_subdirectory (deconv)
else (F2PY_EXECUTABLE)
  message (SEND_ERROR "ERROR: Missing f2py executable!")
endif (F2PY_EXECUTABLE)

if (WCSLIB_FOUND)
  if (BOOST_FOUND)
    add_subdirectory (python-wcslib)
  else (BOOST_FOUND)
    message (SEND_ERROR "ERROR: Missing Boost++ library - needed for python-wcslib!")
  endif (BOOST_FOUND)
else (WCSLIB_FOUND)
  message (SEND_ERROR "ERROR: Missing WCS library - needed for python-wcslib!")
endif (WCSLIB_FOUND)
