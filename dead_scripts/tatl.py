# -*- coding: utf-8 -*-

#History: tatl: whilst using Mercury computers (parallel processing farms) they used a briilliant tool
#to keep track of the timing between processing activities . This is not that tool, just homage.
#... this activity reminded me of the tool...
#TATL = trace analysis tool and Library
import gc
gc.disable()

filo = False
if not filo:
    tl = open ("tatlgash", "w") #local users directory, overwritten each run
    level = 0
    nested = []
    filo = True
    

import sys
sys.setrecursionlimit(64000)
#outer functions pay an additional penalty of the inner calls to this tatl function
# so either avoid tatling outer functions, or don't include any inner tatled functions
# the stack frame represents context so local st and local end are on that call's stack
# a vague attempt at indenting has  been  done  in the tatlgash


#   -------------------------To Use -----------------------------------------------------------
# ensure:  from tatl import tatl
# above function/member to be monitored  add decorator @tatl
#@tatl
#def extract ().....
#
# will write a file called tatlgash into local  directory
# to process the files use  analyse_timing.py  - gives a summary
# -----------------------------------------------------------------------------------------------------


import time
def tatl (f):
    def new_f(*args, **kwds):
         global level
         level +=1
         cnt = level
         tb = ""
         while cnt > 0:
            tb +='\t'
            cnt -=1
         st = time.time()
         if f.__name__ == '__init__' :    # and  args[0].__class__  == 'class'
             ln = (str(st) + tb + str(args[0].__class__) + " " + f.__name__ + " " )
         else:
             ln = (str(st)+ tb + f.__name__+  " "   )
         try:
            res = f (*args,**kwds)
         except Exception, e :
            exc_type, exc_obj, exc_tb = sys.exc_info()
            level -=1
            end = time.time()
            ln +=   ( str("%.16f" % (end -st)) + "\n")
            nested.append(ln)
            return None
         end = time.time()
         ln +=   (str("%.16f" % (end -st)) + "\n" )
         tl.write(ln) 
         level -=1
         return res
    return new_f
    
def fintatl(f):
    def newf(*args, **kwds):
        res =  f (*args,**kwds)
        tl.close()
        return res
    return newf
    
        
        




        
        
        
        
        
        
#if __name__ == '__main__'


