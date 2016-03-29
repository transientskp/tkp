"""
This is a tool for managing a TKP project. It can be used to initialize a TKP
project and the jobs inside a project. To start using this tool you first
create a TraP project by running:

  $ trap-manage.py initproject <projectname>

In the folder where you want to put the TraP project. To learn more about a
specific `trap-manage.py` subcommand, run:

  $ trap-manage.py <subcommand> -h

Have a nice day!
"""
import argparse
import os
from os import path
import shutil
import re
import errno
import getpass
import stat
import sys
import logging
import json
import tkp
from tkp.db.sql.populate import populate
from tkp.main import run

# logging.basicConfig(level=logging.INFO)


class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.

    If this exception is raised during the execution of a management
    command, it will be caught and turned into a nicely-printed error
    message to the appropriate output stream (i.e., stderr); as a
    result, raising this exception (with a sensible description of the
    error) is the preferred way to indicate that something has gone
    wrong in the execution of a command.

    """
    pass


def check_if_exists(filename):
    if not os.access(filename, os.R_OK):
        raise CommandError("can't read %s" % filename)
    return True


def get_template_dir():
    """
    Determines where the job and project templates are.
    """
    return path.join(tkp.__path__[0], 'config')


def make_writeable(filename):
    """
    Make sure that the file is writeable.
    Useful if our source is read-only.
    """
    if not os.access(filename, os.W_OK):
        st = os.stat(filename)
        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
        os.chmod(filename, new_permissions)


def line_replace(substitutes, line):
    """substitutions - list of 2 item tuples.
    every occurance of the first item in the tuple in line will be replaces
    with the second. The to be replaced thingy should be in Django
    template format e.g. {% user_name %}
    template format e.g. {% user_name %}
    """
    for pattern, repl in substitutes:
        line = re.sub("{%\s*" + pattern + "\s*%}", repl, line)
    return line


def copy_template(job_or_project, name, target=None, **options):
    """
    this is taken from django/core/management/templates.py and modified to fit
    our needs
    """
    # If it's not a valid directory name.
    if not re.search(r'^[_a-zA-Z][\w\-]*$', name):
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', name):
            message = ('make sure the name begins '
                       'with a letter or underscore')
        else:
            message = 'use only numbers, letters and underscores'
        raise CommandError("%r is not a valid %s name. Please %s." %
                           (name, job_or_project, message))

    # if some directory is given, make sure it's nicely expanded
    if target is None:
        top_dir = path.join(os.getcwd(), name)
        try:
            os.makedirs(top_dir)
        except OSError, e:
            if e.errno == errno.EEXIST:
                message = "'%s' already exists" % top_dir
            else:
                message = e
            raise CommandError(message)
    else:
        top_dir = os.path.abspath(path.expanduser(target))
        if not os.path.exists(top_dir):
            raise CommandError("Destination directory '%s' does not "
                               "exist, please create it first." % top_dir)

    base_name = '%s_name' % job_or_project
    base_subdir = '%s_template' % job_or_project
    base_directory = '%s_directory' % job_or_project

    template_dir = os.path.join(get_template_dir(), base_subdir)
    prefix_length = len(template_dir) + 1

    # these are used for string replacement in templates
    substitutes = (
        ("user_name", getpass.getuser()),
        # ("runtime_directory", top_dir)
    )

    for root, dirs, files in os.walk(template_dir):

        path_rest = root[prefix_length:]
        relative_dir = path_rest.replace(base_name, name)
        if relative_dir:
            target_dir = path.join(top_dir, relative_dir)
            if not path.exists(target_dir):
                os.mkdir(target_dir)

        for dirname in dirs[:]:
            if dirname.startswith('.'):
                dirs.remove(dirname)

        for filename in files:
            if filename.endswith(('.pyo', '.pyc', '.py.class')):
                # Ignore some files as they cause various breakages.
                continue
            old_path = path.join(root, filename)
            new_path = path.join(top_dir, relative_dir,
                                 filename.replace(base_name, name))
            if path.exists(new_path):
                raise CommandError("%s already exists, overlaying a "
                                   "project or job into an existing "
                                   "directory won't replace conflicting "
                                   "files" % new_path)

            with open(old_path, 'r') as template_file:
                content = template_file.read()

            if content:
                content = line_replace(substitutes, content)

            with open(new_path, 'w') as new_file:
                new_file.write(content)

            print "Creating %s" % new_path
            try:
                shutil.copymode(old_path, new_path)
                make_writeable(new_path)
            except OSError:
                sys.stderr.write(
                    "Notice: Couldn't set permission bits on %s. You're "
                    "probably using an uncommon filesystem setup. No "
                    "problem.\n" % new_path)
    return top_dir


def parse_monitoringlist_positions(args, str_name="monitor_coords",
                                   list_name="monitor_list"):
    """Loads a list of monitoringlist (RA,Dec) tuples from cmd line args object.

    Processes the flags "--monitor-coords" and "--monitor-list"
    NB This is just a dumb function that does not care about units,
    those should be matched against whatever uses the resulting values...
    """
    monitor_coords = []
    if hasattr(args, str_name) and getattr(args, str_name):
        try:
            monitor_coords.extend(json.loads(getattr(args, str_name)))
        except ValueError:
            logging.error("Could not parse monitor-coords from command line:"
                          "string passed was:\n%s" % (getattr(args, str_name),)
                          )
            raise
    if hasattr(args, list_name) and getattr(args, list_name):
        try:
            mon_list = json.load(open(getattr(args, list_name)))
            monitor_coords.extend(mon_list)
        except ValueError:
            logging.error("Could not parse monitor-coords from file: "
                          + getattr(args, list_name))
            raise
    return monitor_coords


def init_project(args):
    print "creating project '%s'" % args.name
    return copy_template("project", args.name, args.target)


def init_job(args):
    print "creating job '%s'" % args.name
    return copy_template("job", args.name)


def prepare_job(jobname):
    here = os.getcwd()
    jobdir = os.path.join(here, jobname)
    pipelinefile = os.path.join(here, "pipeline.cfg")
    sys.path.append(jobdir)


def run_job(args):
    print "running job '%s'" % args.name
    prepare_job(args.name)
    monitor_coords = parse_monitoringlist_positions(args)
    run(args.name, monitor_coords)


def init_db(options):
    from tkp.config import initialize_pipeline_config, get_database_config
    cfgfile = os.path.join(os.getcwd(), "pipeline.cfg")
    if os.path.exists(cfgfile):
        pipe_config = initialize_pipeline_config(cfgfile, "notset")
        dbconfig = get_database_config(pipe_config['database'], apply=False)
    else:
        dbconfig = get_database_config(None, apply=False)

    dbconfig['yes'] = options.yes
    dbconfig['destroy'] = options.destroy

    populate(dbconfig)


def get_parser():
    trap_manage_note = """
        A tool for managing TKP projects.

        Use 'initproject' to create a project directory. Other Subcommands
        should be run from within a project directory.

        NB:
        To overwrite the database settings in pipeline.cfg you can use these
        environment variables to configure the connection:

        * TKP_DBENGINE
        * TKP_DBNAME
        * TKP_DBUSER
        * TKP_DBPASSWORD
        * TKP_DBHOST
        * TKP_DBPORT

        (This is useful for setting up test databases, etc.)

        """

    parser = argparse.ArgumentParser(
        description=trap_manage_note,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser_subparsers = parser.add_subparsers()

    # initproject
    initproject_parser = parser_subparsers.add_parser(
        'initproject',
        help="""
        Initialize a pipeline project directory, complete with config files which you
        can use to configure your pipeline.
        """)
    initproject_parser.add_argument('name', help='project folder name')
    initproject_parser.add_argument('-t', '--target',
                                    help='location of new TKP project')
    initproject_parser.set_defaults(func=init_project)

    # initjob
    initjob_parser = parser_subparsers.add_parser(
        'initjob',
        help="""
        Create a job folder, complete with job-specific config files
        which you will need to modify.
        """)
    initjob_parser.add_argument('name', help='Name of new job')
    initjob_parser.set_defaults(func=init_job)

    # runjob
    run_parser = parser_subparsers.add_parser(
        'run',
        help="Run a job by specifying the name of the job folder.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    run_parser.add_argument('name', help='Name of job to run')
    m_help = ('a list of RA,DEC coordinates to monitor in JSON format, '
              '(decimal degrees)'
              ' example: "[[5, 6], [7, 8]]"')
    run_parser.add_argument('-m', '--monitor-coords', help=m_help)
    run_parser.add_argument('-l', '--monitor-list',
                            help='Specify a file containing the '
                                 'JSON-formatted monitor co-ordinates.')
    run_parser.set_defaults(func=run_job)

    # initdb
    initdb_parser = parser_subparsers.add_parser(
        'initdb',
        help="Initialize a database with the TKP schema.")
    initdb_parser.add_argument('-y', '--yes',
                               help="don't ask for confirmation",
                               action="store_true")
    initdb_parser.add_argument('-d', '--destroy',
                               help="remove all tables before population"
                                    "(only works with Postgres backend)",
                               action="store_true")
    initdb_parser.set_defaults(func=init_db)
    return parser


def main():
    args = get_parser().parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
