set(SOURCE_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/deconv.f
)

add_custom_command(
  OUTPUT
    deconv.so
  DEPENDS ${SOURCE_FILES}
  COMMAND ${F2PY_EXECUTABLE} -m deconv -c ${SOURCE_FILES}
)

install (FILES ${CMAKE_CURRENT_BINARY_DIR}/deconv.so DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)

