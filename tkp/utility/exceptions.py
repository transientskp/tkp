"""

This module defines exceptions specific to the TKP package

"""



class TKPException(Exception):
    """General TKP exception"""
    
#    def __init__(self, value):
#        self.value = value
#
#    def __str__(self):
#        return repr(self.value)


class TKPDataBaseError(TKPException):
    """Database exceptions specific to the TKP"""

    pass


    

def main():
    try:
        print '1'
        raise TKPException('TKP error')
        print '2'   # never get here
    except TKPException, e:
        print 'caught:', e
    try:
        print '3'
        print TKPDataBaseError('database not enabled')
        print '4'  # never get here
    except TKPDataBaseError, e:
        print 'caught:', e
    try:
        print '5'
        print TKPDataBaseError('database not enabled')
        print '6'  # never get here
    except TKPExceptin, e:
        print 'caught:', e
        
if __name__ == '__main__':
    main()
