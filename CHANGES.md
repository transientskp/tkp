# Changelog
-----------

##4.0 release candidate 1

### frequency band logic change

the band determination logic has changed. Before all bands where split
into 1 MHz intervals and associated as such. With this release  images
are put in the same band if their bandwidths overlap.

We added an option to limit the bandwidth used for band association
([#492][]). Limiting the bandwidth for an image is done by
setting `bandwidth_max` in *job_params.cfg* under the
`persistence section`. E.g.::

    [persistence]
    bandwidth_max = 0.0

Setting the value to 0.0 will use the bandwidth defined in the image
headers, a non 0.0 value will override this value.

[#492]: https://github.com/transientskp/tkp/issues/492


### added streaming telescope support

The internals of TraP have been rewritten to support streaming AARTFAAC
data ([#483][]). There is now a new section in the job_params.cfg file
with a mode setting. Setting this to batch will keep the old TraP
behavior, but setting mode to stream will enable the new behavior.
TraP will connect to a network port and process these images untill
terminated.
The hosts and ports where to connect to is controlled with the hosts
and ports settings::

    [pipeline]
    mode = 'stream'
    hosts = 'struis.science.uva.nl,struis.science.uva.nl'
    ports = '6666,6667'

The batch mode should mostly be unaffected, only the order of actions
has changed. TraP will process the full dataset now in chunks grouped by
timstamp. Tthe storing of images, quality checks and meta data
extraction is now run together with the source extraction and assocation
cycle, where before this was all done at the start of a TraP run.
This makes it more similar to how we process streaming data and enabled
other optimisations in the future.

[#483]: https://github.com/transientskp/tkp/pull/483


### Removal of MongoDB image store

If you enable the ``copy_images`` setting in your pipeline.cfg file
the images are now stored in the sql database ([#534][]). This makes it
much easier to manage the files, for example delete them. Also the
images load faster in banana. This makes setting up and configuring
MongoDB obsolete. 


[#534]: https://github.com/transientskp/tkp/pull/534


### Add command line option to delete dataset

It is now possible to delete a dataset  ([#533][])::


    $ trap-manage.py deldataset 5 -y

    dataset 5 has been deleted!


[#533]: https://github.com/transientskp/tkp/pull/533


### Make TraP more resilient against faulty data

TraP often crashed on faulty image data. On popular request TraP will
now try to continue, giving a warning. [#522][]

[#522]: https://github.com/transientskp/tkp/issues/522


### Various other changes and bugfixes

* Fix Numpy 1.9+ compatibility [#509][])
* TraP sourcefinder error on updated AARTFAAC images [#505][]
* forced fits is not parallelised [#526][]
* restructure logging, make less verbose. Also multiproc workers will
  log to stdout.
* fix multiprocess job cancelling problem (ctrl-c)

[#509]: https://github.com/transientskp/tkp/issues/509
[#505]: https://github.com/transientskp/tkp/issues/505
[#526]: https://github.com/transientskp/tkp/issues/526


### known issues

* Streaming mode gives a harmless error [#536][]
* Alembic upgrade is not working yet [#535][]


[#535]: https://github.com/transientskp/tkp/issues/535
[#536]: https://github.com/transientskp/tkp/issues/536


## R3.1.1 (2016-05-20)

Adds a 'generic' (i.e. not telescope-specific) quality check for flat images,
which are clearly bad data since they contain no information ([#507][]).
Also makes some changes to the way image-rejection reasons are handled, 
closing [#360][] in the process.

[#360]: https://github.com/transientskp/tkp/issues/360
[#507]: https://github.com/transientskp/tkp/issues/507

## R3.1 (2016-03-29)
Adds an uncommon but potentially serious bug-fix, and
some minor user-interface improvements.

### User-interface changes
New boolean entry `colorlog` in *pipeline.cfg* ([#502][]),
this controls whether the console logging-output from *trap-manage.py*
is colored according to message severity. E.g.:

    [logging]
    colorlog = True

This is accompanied by some adjustments to the logging, we now output both
INFO and DEBUG level logfiles (under the *<jobdir>/logs/<run_datestamp>* folders).

### Bugfixes
- Catch some forced fitting bugs that could possibly have been encountered
  due to oversize 'skyregion' settings, or simply when reducing mosaic images
  with 'NaN' pixel regions. ([#496][])

### Documentation
- Add ['features overview'](http://tkp.readthedocs.org/en/latest/introduction.html#key-features)
  section to docs.
- Document use (and units) of 'monitoring-coords' option to *trap-manage.py*.
  ([#485][])

[#485]: https://github.com/transientskp/tkp/issues/485
[#496]: https://github.com/transientskp/tkp/pull/496
[#502]: https://github.com/transientskp/tkp/pull/502



## R3.0 (2016-01-15)

No changes since R3.0rc


## R3.0rc (2015-12-14)

### User-interface changes
New entry `expiration` in *job_params.cfg* ([#472][]):

    [source_extraction]
    expiration = 10  ; number of forced fits performed after a blind fit


### Features / Enhancements
- Added support for AARTFAAC format images ([#444][], [#452][]).
- Expiration of forced-fit monitoring at locations with no recent blind
  detections ([#472][]).
- Caching of additional variability metrics (`varmetric` table) to improve
  interactive queries via the 'Banana' web-interface ([#469][]).


### Refactoring / Infrastructure changes
- Started integrating SQLAlchemy as a future replacement for home-grown
  database-ORM code ([#362][]).
- Migrate from PyFITS to astropy.io.fits ([#355][]).
- Removed unused 'Celery' code ([#433][]).


[#355]: https://github.com/transientskp/tkp/issues/355
[#362]: https://github.com/transientskp/tkp/issues/362
[#433]: https://github.com/transientskp/tkp/issues/433
[#444]: https://github.com/transientskp/tkp/issues/444
[#452]: https://github.com/transientskp/tkp/pull/452
[#469]: https://github.com/transientskp/tkp/pull/469
[#472]: https://github.com/transientskp/tkp/pull/472



## R2.1 (2015-07-14)
A minor release, database-schema compatible with R2.0.
A comprehensive listing of 
[closed issues](https://github.com/transientskp/tkp/issues?utf8=%E2%9C%93&q=+milestone%3A2.1+is%3Aissue) and 
[merged pull requests](https://github.com/transientskp/tkp/issues?utf8=%E2%9C%93&q=+milestone%3A2.1+is%3Amerged) 
can be found on the issue tracker,
but the summary is as follows:

### User-interface changes
Minor changes to *job_params.cfg*,
- The ``[persistence]`` variables ``sigma`` and ``f`` have been renamed to ``rms_est_sigma`` and 
``rms_est_fraction`` respectively ([#435][]).
- The ``[association]`` section has a new variable, ``beamwidths_limit``, to control the hard-limit
on source-association ([#421][], [#447][]).

### Features / Enhancements
- We now calculate and store 'goodness-of-fit' metrics for all source-extractions ([#429][]).
- The hard limit on source-association radius is now a user-configurable parameter ([#421][], [#447][]).
This resulted from investigation of issues with source association when large systematic position-errors are present.
- We now support AMI-LA data in CASA image format, in addition to FITS ([#438][]).

### Bugfixes 
- We now perform additional 'VACUUM' cleanups on the Postgres database, to improve performance ([#432][], [#441][]).
- Setup procedure now pulls in dependencies, allowing use of ``pip install tkp`` without a source-checkout ([#393][]).
- Docfixes ([#442][]).
- Header injection now works with CASA format images ([#425][]).

### Refactoring / Infrastructure changes
Most refactoring is on hold for now, but some minor changes were deemed desirable to enable new features.
We also took steps to make the TKP docs-hosting and testing infrastructure less reliant on privately administered UvA machines.
- Reworked DataAccessor interface classes for shorter, simpler accessors ([#424][], [#426][]).
- Migrated docs hosting to [tkp.readthedocs.org](http://tkp.readthedocs.org).
- Added [Travis-CI testing](https://travis-ci.org/transientskp/tkp) ([#437][], [#439][]).


[#393]: https://github.com/transientskp/tkp/issues/393
[#421]: https://github.com/transientskp/tkp/issues/421
[#424]: https://github.com/transientskp/tkp/issues/424
[#425]: https://github.com/transientskp/tkp/issues/425
[#426]: https://github.com/transientskp/tkp/issues/426
[#429]: https://github.com/transientskp/tkp/issues/429
[#432]: https://github.com/transientskp/tkp/issues/432
[#435]: https://github.com/transientskp/tkp/issues/435
[#437]: https://github.com/transientskp/tkp/issues/437
[#438]: https://github.com/transientskp/tkp/issues/438
[#439]: https://github.com/transientskp/tkp/issues/439
[#441]: https://github.com/transientskp/tkp/issues/441
[#442]: https://github.com/transientskp/tkp/issues/442
[#447]: https://github.com/transientskp/tkp/issues/447



## R2.0 (2014-12-16)
First public release.
See the [R2 docs](http://tkp.readthedocs.org/en/release2/) and the
[TraP paper](http://adsabs.harvard.edu/abs/2015arXiv150301526S) for a full
desription.
