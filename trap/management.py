"""
This is a tool for managing a TRAP project. It can be used to initialize a
TRAP project and manage (init, clean, remove) its containing jobs.

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
import trap


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


def parse_arguments():
    parser = argparse.ArgumentParser(description='This is a tool for managing a TRAP project', epilog=__doc__)
    parser_subparsers = parser.add_subparsers()

    initproject_parser = parser_subparsers.add_parser('initproject')
    initproject_parser.add_argument('initprojectname', help='project folder name')
    initproject_parser.add_argument('--target', help='location of new TRAP project')

    initjob_parser = parser_subparsers.add_parser('initjob')
    initjob_parser.add_argument('initjobname', help='Name of new job')

    initjob_parser = parser_subparsers.add_parser('run')
    initjob_parser.add_argument('runjobname', help='Name of job to run')

    initjob_parser = parser_subparsers.add_parser('runlocal')
    initjob_parser.add_argument('runlocaljobname', help='Name of job to run ('
                                                        'local run)')

    clean_parser = parser_subparsers.add_parser('clean')
    clean_parser.add_argument('cleanjobname', help='Name of job to clean')

    info_parser = parser_subparsers.add_parser('info')
    info_parser.add_argument('infojobname', help='Name of job to print info of')

    parsed = vars(parser.parse_args())
    return parsed


def get_template_dir():
    """
    Determines where the job and project templates are.
    """
    return path.join(trap.__path__[0], 'conf')


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
    every occurance of the first item in the tuple in line will be replaces with the second

    the to be replaced thingy should be in Django template format e.g. {% user_name %}
    """
    for pattern, repl in substitutes:
        line = re.sub("{%\s*" + pattern + "\s*%}", repl, line)
    return line


def copy_template(job_or_project, name, target=None, **options):
    """
    this is taken from django/core/management/templates.py and modified to fit our needs
    """
    # If it's not a valid directory name.
    if not re.search(r'^[_a-zA-Z]\w*$', name):
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


def init_project(projectname, target=None):
    print "creating project '%s'" % projectname
    return copy_template("project", projectname, target)


def init_job(jobname, target=None):
    print "creating job '%s'" % jobname
    return copy_template("job", jobname, target)

def prepare_job(jobname):
    here = os.getcwd()
    jobdir = os.path.join(here, jobname)
    pipelinefile = os.path.join(here, "pipeline.cfg")
    tasksfile = os.path.join(here, "tasks.cfg")
    sys.path.append(jobdir)
    sys.argv += ["-d", "-c", pipelinefile, "-t", tasksfile, "-j", jobname]

def run_job(jobname):
    print "running job '%s'" % jobname
    prepare_job(jobname)
    import trap.run.distributed
    sys.exit(trap.run.distributed.Trap().main())

def runlocal_job(jobname):
    print "running job '%s' (local)" % jobname
    prepare_job(jobname)
    import trap.run.local
    sys.exit(trap.run.local.TrapLocal().main())

def clean_job(jobname):
    here = os.getcwd()
    statefile = os.path.join(here, jobname, "statefile")
    if os.access(statefile, os.R_OK):
        print "Removing state file for job %s" % jobname
        os.unlink(statefile)
    else:
        print "no statefile for job %s" % jobname


def info_job(jobname):
    print "TODO: print info about job %s" % jobname


def main():
    parsed = parse_arguments()
    if parsed.has_key('initprojectname'):
        target = parsed.get('target', '')
        init_project(parsed['initprojectname'], target)
    elif parsed.has_key('initjobname'):
        init_job(parsed['initjobname'])
    elif parsed.has_key('cleanjobname'):
        clean_job(parsed['cleanjobname'])
    elif parsed.has_key('infojobname'):
        info_job(parsed['infojobname'])
    elif parsed.has_key('runjobname'):
        run_job(parsed['runjobname'])
    elif parsed.has_key('runlocaljobname'):
        runlocal_job(parsed['runlocaljobname'])
    else:
        parsed.print_help()


if __name__ == '__main__':
    main()
