"""
This is a tool for managing a TRAP runtime project.

It can be used to initialize a runtime project and manage (init, clean, remove) its jobs
"""
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Manage your TRAP runtime project')
    parser_subparsers = parser.add_subparsers()
    initproject_parser = parser_subparsers.add_parser('initproject')
    initproject_parser.add_argument('initprojectname', help='project folder name')
    initjob_parser = parser_subparsers.add_parser('initjob')
    initjob_parser.add_argument('initjobname', help='Name of new job')
    clean_parser = parser_subparsers.add_parser('clean')
    clean_parser.add_argument('cleanjobname', help='Name of job to clean')
    info_parser = parser_subparsers.add_parser('info')
    info_parser.add_argument('infojobname', help='Name of job to print info of')
    parsed = vars(parser.parse_args())
    return parsed

def initproject(projectname):
    print "TODO: initing project %s" % projectname

def initjob(jobname):
    print "TODO: initing job %s" % jobname

def cleanjob(jobname):
    print "TODO: cleaning job %s" % jobname

def infojob(jobname):
    print "TODO: print info about job %s" % jobname

def main():
    parsed = parse_arguments()

    if parsed.has_key('initprojectname'):
        initproject(parsed['initprojectname'])
    if parsed.has_key('initjob'):
        initjob(parsed['initjob'])
    if parsed.has_key('cleanjob'):
        cleanjob(parsed['cleanjob'])
    if parsed.has_key('infojob'):
        cleanjob(parsed['infojob'])

if __name__ == '__main__':
    main()