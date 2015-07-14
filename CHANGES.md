# Changelog
---------------

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
``rms_est_fraction`` respectively (#435).
- The ``[association]`` section has a new variable, ``beamwidths_limit``, to control the hard-limit
on source-association (#421, #447).

### Features / Enhancements
- We now calculate and store 'goodness-of-fit' metrics for all source-extractions (#429).
- The hard limit on source-association radius is now a user-configurable parameter (#421, #447).
This resulted from investigation of issues with source association when large systematic position-errors are present.
- We now support AMI-LA data in CASA image format, in addition to FITS (#438).

### Bugfixes 
- We now perform additional 'VACUUM' cleanups on the Postgres database, to improve performance (#432, #441).
- Setup procedure now pulls in dependencies, allowing use of ``pip install tkp`` without a source-checkout (#393).
- Docfixes (#442).
- Header injection now works with CASA format images (#425).

### Refactoring / Infrastructure changes
Most refactoring is on hold for now, but some minor changes were deemed desirable to enable new features.
We also took steps to make the TKP docs-hosting and testing infrastructure less reliant on privately administered UvA machines.
- Reworked DataAccessor interface classes for shorter, simpler accessors (#424, #426).
- Migrated docs hosting to [tkp.readthedocs.org](http://tkp.readthedocs.org).
- Added [Travis-CI testing](https://travis-ci.org/transientskp/tkp) (#437, #439).

--------

## R2.0 (2014-12-16)
First public release.
See the [R2 docs](http://tkp.readthedocs.org/en/release2/) and the
[TraP paper](http://adsabs.harvard.edu/abs/2015arXiv150301526S) for a full
desription.