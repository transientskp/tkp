include_directories( ${Boost_INCLUDE_DIRS})

include_directories (${PYTHON_INCLUDE_DIRS})

if (WCSLIB_INCLUDES)
  include_directories (
    ${WCSLIB_INCLUDES}
    )
endif (WCSLIB_INCLUDES)

add_library (wcslib MODULE wcslib.cpp)

target_link_libraries (wcslib ${WCSLIB_LIBRARIES} ${Boost_PYTHON_LIBRARY})
set_target_properties(wcslib
  PROPERTIES
  PREFIX ""
#  LINK_FLAGS "-undefined dynamic_lookup"
  )

## Linker instructions

if (APPLE)
  set_target_properties (wcslib
    PROPERTIES
    LINK_FLAGS "-undefined dynamic_lookup"
    )
else (APPLE)
  set_target_properties (wcslib
    PROPERTIES
    LINK_FLAGS "-shared"
    )
endif (APPLE)


install (TARGETS wcslib DESTINATION ${PYTHON_PACKAGES_DIR})
