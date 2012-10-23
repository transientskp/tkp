configure_file(pyse.cmake pyse @ONLY)
install (PROGRAMS ${CMAKE_BINARY_DIR}/enduser_scripts/pyse DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)
install (FILES pyse.py DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)
