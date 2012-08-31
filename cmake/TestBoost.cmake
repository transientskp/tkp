
##_____________________________________________________________________________
## Test Boost library for library version <major.minor.release>

## Locate test program
find_file (TEST_BOOST_CC TestBoost.cc
  PATHS ${PROJECT_SOURCE_DIR}
  PATH_SUFFIXES cmake Modules
  )

if (BOOST_INCLUDES AND BOOST_LIBRARIES AND TEST_BOOST_CC)
  try_run(BOOST_VERSION_RUN_RESULT BOOST_VERSION_COMPILE_RESULT
    ${PROJECT_BINARY_DIR}
    ${TEST_BOOST_CC}
    COMPILE_DEFINITIONS -I${BOOST_INCLUDES}
    RUN_OUTPUT_VARIABLE BOOST_VERSION_OUTPUT
    )
endif (BOOST_INCLUDES AND BOOST_LIBRARIES AND TEST_BOOST_CC)

## Comile of test program successful?
if (BOOST_VERSION_COMPILE_RESULT)
  ## Run of test program successful?
  if (BOOST_VERSION_RUN_RESULT AND BOOST_VERSION_OUTPUT)

    ## Library version _________________________

    string(REGEX REPLACE "BOOST_VERSION ([0-9]+).*" "\\1" BOOST_VERSION ${BOOST_VERSION_OUTPUT})
    string(REGEX REPLACE ".*BOOST_VERSION_MAJOR ([0-9]+).*" "\\1" BOOST_VERSION_MAJOR ${BOOST_VERSION_OUTPUT})
    string(REGEX REPLACE ".*BOOST_VERSION_MINOR ([0-9]+).*" "\\1" BOOST_VERSION_MINOR ${BOOST_VERSION_OUTPUT})
    string(REGEX REPLACE ".*BOOST_VERSION_PATCH ([0-9]+).*" "\\1" BOOST_VERSION_PATCH ${BOOST_VERSION_OUTPUT})

  else (BOOST_VERSION_RUN_RESULT AND BOOST_VERSION_OUTPUT)
    message (FATAL_ERROR "[Boost] Failed to run TestBoost!")
  endif (BOOST_VERSION_RUN_RESULT AND BOOST_VERSION_OUTPUT)
else (BOOST_VERSION_COMPILE_RESULT)
  message (FATAL_ERROR "[Boost] Failed to compile TestBoost!")
endif (BOOST_VERSION_COMPILE_RESULT)

## Assemble full version of library
set (BOOST_VERSION "${BOOST_VERSION_MAJOR}.${BOOST_VERSION_MINOR}.${BOOST_VERSION_PATCH}")

