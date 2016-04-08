# Changelog
-----------

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
