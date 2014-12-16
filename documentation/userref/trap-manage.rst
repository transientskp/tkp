.. _trap-manage:

++++++++++++++
trap-manage.py
++++++++++++++

``trap-manage.py`` is the command-line tool for initialising and running the
TraP pipeline. Different tasks are handled via the use of 'subcommands'
as detailed below.

When the TraP is correctly installed on the system you can issue the
``trap-manage.py`` command. Documentation of subcommands is also available
on the command line. You can use the ``--help`` flag (also per subcommand) to
explore all possible options.

-----

.. argparse::
    :module: tkp.management
    :func: get_parser
    :prog: trap-manage.py

    run : @before
        .. _trap-manage-run:



