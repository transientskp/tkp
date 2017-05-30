

TraP technical notes for the future
===================================

Hi future TraP developer. This is Gijs, the last person who worked on TraP.
In this short document I'm describing the current problems with TraP, what we 
tried to solve it and what could be tried to solve it. There are 2 main issues,
speed and code complexity.

architecture
------------

Currently the main processing logic is defined in tkp.main, which is the 
highest level entrypoint, apart from the CLI handling in tkp.management which
initialises the main loop. i suggest you start exploring the code from here,
use something like pycharm to click trough the various nested steps. i think
all the steps are quite well documented in the TKP documentation.
 
Our distribution code is a bit clunky, this because we wanted to support
multiple map reduce backends. in the end we only use multiprocessing now.
I recommend you run the pipeline in single threaded mode for debugging
and profiling.

Speed
-----

### Database


Current TraP is too slow to process AARTFAAC data in real time. On a fresh
database it is quite snappy, but it will slow down over time. This is because
for every image and corresponding extracted sourced added to the database
TraP does a lot of calculations in the database. Images and extracted sources
data is stored indefinitely. This results in huge tables, which are being
scanned for every image processing cycle. This doesn't scale.

 
The database is the bottleneck, since no queries can be parallelised. This
makes it an important spot to optimise. If we can somehow reduce the amount of
operations performed by the database and minimise the amount of scanning on
tables that could already speed up the whole pipeline.

original idea was to use MonetDB, which is supposed to suffer less from 
slowdowns on huge tables. We tried MonetDB for about 2 years, but we gave up
since it turned out to be unstable as a database platform and it didn't improve
over time. Quite often the database would crash and we would sometimes even suffer
data corruptions.

I'm of the opinion that using MonetDB would have not really solved our problems,
we should have designed the data storage in a different way. I think it is for
example important to implement multi resolution lightcurves. We don't need
second scale lightcurves after a year. That could keep database row count much
lower. We only need a short list of coordinates that required monitoring
(forced fitting) in our case.

Originally the idea was that we are going to work with a massive dataset and
that we need to do the work close to the datase and all the calculations in the
database. This turns out to be a terrible idea. Writing complex SQL queries 
is a pain, having 2 logical code spaces is hard to manage and reason about
and code complexity explodes. It is probably much better to use the database
only as a storage, and do the calculations in memory. The amount of sources
tracked in case of AARTFAAC is quite low, but even if you track 1000 sources
it is probably much better to do this in memory and write only the lightcurves 
to the database. The logic becomes much more compact and is much easier to maintain.

Ideally I would move TraP to a more service oriented design, where a socket
listener dumps images on a subscribably channel. Then a source extracter
extracts sources and publishes this on a different channel. Same for a source
associator. This way you can 'plug in' modules, like a 'transient finder'
that listens to a lightcurve stream. or a 'database dumper' that records
lighcurves to a database. That way nonthing needs to wait for eachother, 
it scales to multiple machines, no synchronisation is needed between workers
and everything is implicility parallel.

### pipeline

Various tasks (not DB) can be executed in parallel. We already do that for
the images of different bands within one time step. We do a map reduce using
Python multiprocessing. But various steps themselfs can also run in parallel.
For example images of timestep n+1 can already be opened and quality checked,
while the database operations of timestep n are still running. The best
way to accomplish this in my opinion is the rewrite the main logic as a
Directed Acyclic Graph. I'm hearing a lot of good stories about dask
distribute [2]. basically you define tasks and their data dependencies between
them, the scheduler will take care of handling the intermediate results and
scheduling the tasks. 

code complexity
---------------

TraP is a typical largish scientific piece of software where various people
with different opinions have worked on. If you look at this history on git
you can see that the last years we removed more lines of code than we added.

In the beginning there was a homebrew ORM, which turned out to be quite hard
to debug and modify. It is still there, but that is mostly because the test
suite depends on it and we never got around rewriting the test suite.

We then switched to raw SQL queries. We wrote a SQL templating engine, since 
we wanted to support both PostgreSQL and MonetDB, but the SQL syntax of these
engines differs slightly. We then decided to drop MonetDB support, we just 
didn't have the resources and some of us were really unsatisfied with MonetDB.

This enables us to add SQLAlchemy support. This is a better ORM, would simplify
interactive exploration of the database and would enable alembic migrations
between releases. Alembic support is sort of there since 4.0, but we didn't
have made a new release since, so there are no migrations paths yet.

Some of the queries are quite long and quite a mindfuck, almost like solving
a rubiks cube. We tried to rewrite them in SQLAlchemy to make them easier to
handle, but in the end I'm not sure if it helps a lot. A good example is
tkp.db.alchemy.varmetric.py. This is fully Python/SQLAlchemy. it is much
easier to split up queries, add comments, do automatic type conversion and
structure the code. But in the end it renders too SQL. Some people don't like
this, I sort of like it.

I think the biggest problem is that we try to do too much in SQL. Idea was to
minimise traffic between the TraP instance and the database. But this results
in monster queries which are hard to maintain and debug. Probably the solution
lies somewhere ni the middle, try to minimise the traffic, but at the same time
keep query maintainability in mind. probably a lot of queries can be simplified
and becoming slightly quicker by using something like q3c [1]. We never started
using q3c since we wanted to maintain support for MonetDB, something I think
now, harmed progress.


### Banana

banana is the Django based frontend for TraP. In the beginning we also
supported MonetDB, so we even wrote our own MonetDB backend for Django [3].
users think banana is awesome, but for the developers it is a lot of work
to maintain it. The ORM used is different than used by TraP itself, so many
queries have to be rewritten. Also when the database schema changes banana
needs to be updated. This makes it hard to deploy and maintain various versions.

My plan was to move awya from banana in the long run, and give more power to
the end user. let them work with Jupyter Notebooks, let them do queries using
the SQLAlchemy interface we have now, and let them visualise everything with
pandas, seaborn, matplotlib etc. All the parts are there, there are some
example notebooks, but in the end I guess the astronomers find it too complex
to actually work this way, and the prefer Banana.

That is an other problem, Banana can be quite slow from time to time. Sometimes
it is a query, sometimes it is the templating system that just becomes too slow.
Al these problems are maybe not that hard to fix, but take up a lot of time.
Traditional web service methods like caching don't really apply, since our use
cases are quite different (few users, a lot of data). 



 * [1] https://github.com/segasai/q3c
 * [2] https://distributed.readthedocs.io
 * [3] https://github.com/gijzelaerr/djonet
