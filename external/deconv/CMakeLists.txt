add_custom_target (deconv
  ALL
  COMMAND ${F2PY_EXECUTABLE} -m deconv -c ${CMAKE_CURRENT_SOURCE_DIR}/deconv.f
  DEPENDS deconv.f
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Compiling deconv.f ..."
  SOURCES deconv.f
  )

install (FILES deconv.so 
	 DESTINATION ${PYTHON_LOCAL_PACKAGE_DIR})
