# Copy the MonetDB scripts into the database subdirectory; 
# ignore the .svn subdirs

install (DIRECTORY .
    DESTINATION ${CMAKE_INSTALL_PREFIX}/database/sql
    FILES_MATCHING PATTERN "*.sql"
    PATTERN ".svn" EXCLUDE
    )
#install (DIRECTORY .
#    DESTINATION ${CMAKE_INSTALL_PREFIX}/database
#    FILES_MATCHING PATTERN "*.sh"
#    PATTERN ".svn" EXCLUDE
#    )
install (FILES batch
    DESTINATION ${CMAKE_INSTALL_PREFIX}/database/sql
    )
#install (FILES ../setupdb.sh
#    DESTINATION ${CMAKE_INSTALL_PREFIX}/database
#    )

