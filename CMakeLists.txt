add_subdirectory (sql)
add_subdirectory (catalog)

message ("install SETUP SCRIPT in ${CMAKE_INSTALL_PREFIX}...")

install (FILES setup.sh
    DESTINATION ${CMAKE_INSTALL_PREFIX}/database
    )


