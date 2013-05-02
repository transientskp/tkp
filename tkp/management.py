"""
This is a tool for managing a TRAP project. It can be used to initialize a
TKP project and manage (init, clean, remove) its containing jobs.

To start using this tool you first create a TRAP project by running:

 $ trap-manage.py initproject <projectname>

 In the folder where you want to put the TRAP project.
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

import tkp
from tkp.db.sql.populate import populate


logging.basicConfig(level=logging.INFO)

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
    return path.join(tkp.__path__[0], 'conf')


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
    this is taken from django/core/management/templates.py and modified to fit our needs
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
        ("default_username", getpass.getuser()),
        ("runtime_directory", top_dir)
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
                print >> stderr, ("Notice: Couldn't set permission bits on %s. You're "
                                  "probably using an uncommon filesystem setup. No "
                                  "problem.\n" % new_path)


def init_project(args):
    print "creating project '%s'" % args.name
    return copy_template("project", args.name, args.target)


def init_job(args):
    print "creating job '%s'" % args.name
    return copy_template("job", args.name)


def prepare_job(jobname, debug=False):
    here = os.getcwd()
    jobdir = os.path.join(here, jobname)
    pipelinefile = os.path.join(here, "pipeline.cfg")
    tasksfile = os.path.join(here, "tasks.cfg")
    sys.path.append(jobdir)
    if debug:
        # show us DEBUG logging
        sys.argv.append("-d")
    else:
        # show us INFO logging
        sys.argv.append("-v")
    # the lofar pipeline utils parse sys.argv to determine some options
    sys.argv += ["-c", pipelinefile, "-t", tasksfile, "-j", jobname]


def run_job(args):
    print "running job '%s'" % args.name
    prepare_job(args.name, args.debug)
    if args.method == 'cuisine':
        import tkp.distribute.cuisine.run
        sys.exit(tkp.distribute.cuisine.run.Trap().main())
    elif args.method == 'local':
        import tkp.distribute.local.run
        sys.exit(tkp.distribute.local.run.TrapLocal().main())
    elif args.method == 'celery':
        import tkp.distribute.celery
        tkp.distribute.celery.run(args.name)
    elif args.method == 'celerylocal':
        import tkp.distribute.celery
        tkp.distribute.celery.run(args.name, local=True)
    else:
        sys.stderr.write("I don't know what is a %s" % args.method)
        sys.exit(1)


def clean_job(namespace):
    jobname = namespace.name
    here = os.getcwd()
    statefile = os.path.join(here, jobname, "statefile")
    if os.access(statefile, os.R_OK):
        print "Removing state file for job %s" % jobname
        os.unlink(statefile)
    else:
        print "no statefile for job %s" % jobname


def info_job(jobname):
    print "TODO: print info about job %s" % jobname


def init_db(options):
    populate(options)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='This is a tool for managing a TRAP project',
        epilog=__doc__)
    parser_subparsers = parser.add_subparsers()

    # initproject
    initproject_parser = parser_subparsers.add_parser('initproject')
    initproject_parser.add_argument('name', help='project folder name')
    initproject_parser.add_argument('-t', '--target',
                                    help='location of new TKP project')
    initproject_parser.set_defaults(func=init_project)

    # initjob
    initjob_parser = parser_subparsers.add_parser('initjob')
    initjob_parser.add_argument('name', help='Name of new job')
    initjob_parser.set_defaults(func=init_job)

    # runjob
    run_help = """Run a specific job.

For now, use these environment variables to configure the database:

  * TKP_DBENGINE
  * TKP_DBNAME
  * TKP_DBUSER
  * TKP_DBPASS
  * TKP_DBHOST
  * TKP_DBPORT

"""
    run_parser = parser_subparsers.add_parser('run', description=run_help,
                              formatter_class=argparse.RawTextHelpFormatter)

    run_parser.add_argument('name', help='Name of job to run')
    run_parser.add_argument('-d', '--debug', help='enable debug logging',
                            action='store_true')
    m_help = 'Specify a list of RA,DEC co-ordinate pairs to monitor (decimal' \
             ' degrees, no spaces)'
    run_parser.add_argument('-m', '--monitor-coords', help=m_help)
    run_parser.add_argument('-l', '--monitor-list',
                            help='Specify a file containing a list of RA,DEC')
    run_parser.add_argument('-f', '--method', choices=['cuisine',
                                                       'local',
                                                       'celery',
                                                       'celerylocal'],
                            default="cuisine",
                            help="what distribution method to use")
    run_parser.set_defaults(func=run_job)

    #initdb
    initdb_parser = parser_subparsers.add_parser('initdb')
    initdb_parser.add_argument('-d', '--database', help='what database to use',
                               default=getpass.getuser())
    initdb_parser.add_argument('-u', '--user', type=str, help='user')
    initdb_parser.add_argument('-p', '--password', type=str, help='password')
    initdb_parser.add_argument('-H', '--host', type=str, help='host')
    initdb_parser.add_argument('-P', '--port', type=int, help='port',
                               default=0)
    initdb_parser.add_argument('-b', '--backend', choices=["monetdb",
                                                           'postgresql'],
                               default="postgresql",
                               help="what database backend to use")
    initdb_parser.add_argument('-y', '--yes', help="don't ask for confirmation",
                               action="store_true")
    initdb_parser.set_defaults(func=init_db)

    # clean
    clean_parser = parser_subparsers.add_parser('clean')
    clean_parser.add_argument('cleanjobname', help='Name of job to clean')
    clean_parser.set_defaults(func=clean_job)

    # info
    info_parser = parser_subparsers.add_parser('info')
    info_parser.add_argument('infojobname', help='Name of job to print info of')
    info_parser.set_defaults(func=info_job)

    return parser.parse_args()


def main():
    args = parse_arguments()
    args.func(args)


if __name__ == '__main__':
    main()
