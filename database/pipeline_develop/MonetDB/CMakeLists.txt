# Copy the MonetDB scripts into the database subdirectory; 
# ignore the .svn subdirs

install (DIRECTORY .
 	 DESTINATION ${CMAKE_INSTALL_PREFIX}/database
	 FILES_MATCHING PATTERN "*.sql"
  	 PATTERN ".svn" EXCLUDE
	 )
install (DIRECTORY .
 	 DESTINATION ${CMAKE_INSTALL_PREFIX}/database
	 FILES_MATCHING PATTERN "*.batch"
  	 PATTERN ".svn" EXCLUDE
	 )
install (FILES load/update_catalog_locations.bash 
	 DESTINATION ${CMAKE_INSTALL_PREFIX}/database/load
	 )
install (FILES tables/create.table.extractedsources.sh
	 DESTINATION ${CMAKE_INSTALL_PREFIX}/database/tables
	 )
install (CODE
#         "message(\"hello wordl\")")
        "execute_process(
#            COMMAND echo 'Setting up catalog pointers'
            COMMAND bash ${CMAKE_INSTALL_PREFIX}/database/load/update_catalog_locations.bash
#            COMMAND echo 'done'
#	    COMMAND pwd
            WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX}/database/
           )"
        )
