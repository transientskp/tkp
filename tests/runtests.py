#!/usr/bin/env python
"""A small wrapper around nosetests.

Takes care of a '--datapath' argument (see handle_args)
and turns down the monetdb logging level-
this is otherwise disruptive when viewing error messages.
"""
import sys
import nose

def handle_args(args):
    """
    Quick and dirty routine to grab datapath option. Unfortunately optparse
    doesn't play well at passing arguments to a subprocess.
    """
    default_datapath=tkp.config.config['test']['datapath']
    usage = """runtests.py [--datapath=/path/to/test_data] [Standard nosetests args]  
e.g.

"runtests.py --datapath=/path/to/test_data -sv test_database"
                
Default path to TKP test data: {0}
""".format(default_datapath)

    if len(args) == 1:
        print "Usage:"
        print usage
        sys.exit(1)    
    datapath=default_datapath
    if args[1].find("--datapath=")!=-1: #args[0] is script name
        datapath=args[1][len("--datapath="):]
        return datapath, args[0:1]+args[2:]                
    else:
        print "Using default datapath:",datapath
    return datapath, args

if __name__ == "__main__":
    import logging
    try:
        import tkp.config
    except ImportError:
        print """Could not import tkp config, did you run the lofar init.sh?"""
        sys.exit(1)

    datapath, args = handle_args(sys.argv) 
    logging.getLogger('monetdb').setLevel(logging.ERROR) #Suppress MonetDB debug log. 
    logging.getLogger().setLevel(logging.ERROR)
    tkp.config.config['test']['datapath']=datapath
    nose.run(argv=args)


