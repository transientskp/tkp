add_subdirectory (external)
add_subdirectory (tests)

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
