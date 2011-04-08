
if (BOOST_INCLUDES)
  include_directories (${BOOST_INCLUDES})
endif (BOOST_INCLUDES)

if (PYTHON_INCLUDES)
  include_directories (${PYTHON_INCLUDES})
endif (PYTHON_INCLUDES)

if (WCSLIB_INCLUDES)
  include_directories (
    ${WCSLIB_INCLUDES}
    )
endif (WCSLIB_INCLUDES)

add_library (wcslib SHARED wcslib.cpp)

set_target_properties(wcs
  PROPERTIES
  PREFIX ""
#  LINK_FLAGS "-undefined dynamic_lookup"
  )

## Linker instructions

if (APPLE)
  set_target_properties (wcstools
    PROPERTIES
    LINK_FLAGS "-fPIC -bundle -headerpad_max_install_names -undefined dynamic_lookup"
    )
else (APPLE)
  set_target_properties (wcstools
    PROPERTIES
    LINK_FLAGS "-fPIC -shared"
    )
endif (APPLE)


install (TARGETS wcslib
	 DESTINATION ${PYTHON_LOCAL_PACKAGE_DIR})
