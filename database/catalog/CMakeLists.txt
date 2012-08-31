# Copy the MonetDB scripts into the database subdirectory; 
# ignore the .svn subdirs

install (DIRECTORY .
    DESTINATION ${CMAKE_INSTALL_PREFIX}/database/catalog
    FILES_MATCHING PATTERN "*.csv"
    PATTERN ".svn" EXCLUDE
    )
#install (DIRECTORY .
#    DESTINATION ${CMAKE_INSTALL_PREFIX}/database
#    FILES_MATCHING PATTERN "*.sh"
#    PATTERN ".svn" EXCLUDE
#    )
#install (FILES batch
#    DESTINATION ${CMAKE_INSTALL_PREFIX}/database/sql
#    )
#install (FILES ../setupdb.sh
#    DESTINATION ${CMAKE_INSTALL_PREFIX}/database
#    )

