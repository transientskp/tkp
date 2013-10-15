.. _stage-startup:

=========================
Configuration and startup
=========================

Before starting, the :ref:`project and job directories <config-overview>`
should be initialized appropriately, they key configuration files --
``pipeline.cfg``, ``celeryconfig.py``, ``images_to_process.py`` and
``job_params.cfg`` -- should be customized appropriately, and, if required, a
Celery broker and one or more workers shouldbe running. The pipeline is then
started by running::

   $ ./manage.py run <jobname>

from within the project directory.
