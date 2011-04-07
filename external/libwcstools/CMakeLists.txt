
set (libwcstools_sources
  imsetwcs.c imgetwcs.c matchstar.c findstar.c daoread.c wcscon.c
  fitswcs.c wcsinit.c wcs.c ty2read.c webread.c tmcread.c
  gscread.c gsc2read.c ujcread.c uacread.c ubcread.c ucacread.c
  sdssread.c tabread.c binread.c ctgread.c actread.c catutil.c
  skybotread.c imrotate.c fitsfile.c imhfile.c
  hget.c hput.c imio.c dateutil.c imutil.c
  worldpos.c tnxpos.c dsspos.c platepos.c
  sortstar.c platefit.c iget.c fileutil.c
  wcslib.c lin.c cel.c proj.c sph.c wcstrig.c distort.c
  )

## Compiler instructions

add_library (wcstools SHARED
  ${libwcstools_sources}
  )

## Linker instructions

  if (APPLE)
    set_target_properties (wcstools
      PROPERTIES
      LINK_FLAGS "-fPIC -headerpad_max_install_names -undefined dynamic_lookup"
      )
  else (APPLE)
    set_target_properties (wcstools
      PROPERTIES
      LINK_FLAGS "-fPIC -shared"
      )
  endif (APPLE)


install (TARGETS wcstools 
 	 DESTINATION lib)

