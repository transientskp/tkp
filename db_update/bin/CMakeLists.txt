# Copy the Python files into the recipes subdirectory; 
# ignore the .svn subdirs and __init__.py files

install (DIRECTORY .
 	 DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
	 FILES_MATCHING PATTERN "*.py"
  	 PATTERN ".svn" EXCLUDE
	 PATTERN "__init__.py" EXCLUDE
	 )
