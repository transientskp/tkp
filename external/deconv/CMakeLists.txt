set(SOURCE_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/deconv.f
)

add_custom_command(
    OUTPUT deconv.so 
    COMMAND ${F2PY_EXECUTABLE} -m deconv -c ${SOURCE_FILES}
)

add_custom_target(deconv ALL DEPENDS deconv.so) 


install (
    FILES ${CMAKE_CURRENT_BINARY_DIR}/deconv.so
    DESTINATION ${PYTHON_PACKAGES_DIR}
)


